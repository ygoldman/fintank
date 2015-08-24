from __future__ import print_function
import random
import time
import logging

import simplejson as json
from invoke import task, run
from kafka.common import UnknownTopicOrPartitionError
from kafka.client import KafkaClient
from kafka.producer import SimpleProducer
from six.moves import range
from retrying import retry
import collections
import time
import uuid

KAFKA_HOST="streamparse-box:9092"
logging.basicConfig(format='%(asctime)-15s %(module)s %(name)s %(message)s')
log = logging.getLogger()

# model
Ticker = collections.namedtuple('Ticker', ['symbol', 'min','max'])
PortfolioComponent = collections.namedtuple('PortfolioComponent', ['symbol','weight'])

# ranges
tickers = (Ticker(symbol="VTI",min=109.65,max=110.00)
              ,Ticker(symbol="IVE",min=93.79,max=94.20)
              ,Ticker(symbol="IWS",min=73.61,max=74.27)
              )
order_types = ("BUY","SELL")
priorities = (1,2) 

def is_kafka_exception(exception):
    return isinstance(exception, UnknownTopicOrPartitionError)

def random_tick_generator():    
    exchanges = ("NYSE","NASDAQ")
    while True:
        ticker = random.choice(tickers)
        exchange = random.choice(exchanges)
        bid = round(random.uniform(ticker.min, ticker.max), 6)    
        ask = round(random.uniform(bid, ticker.max), 6)
        timestamp = time.time()
        yield {
            "symbol": ticker.symbol,
            "exchange": exchange,
            "bid": bid,
            "ask": ask,
            "timestamp": timestamp 
        }

def random_order_generator():
    while True:
        taxpayer_id = random.randint(1,100) #it's 2009 all over again
        portfolio_order_id = str(uuid.uuid1())
        order_type = random.choice(order_types)
        amount = random.randint(10,500) # small-batch
        portfolio = generate_portfolio()
        priority = 1 #random.choice(priorities) #TODO aggregator
        timestamp = time.time()
        yield {
            "taxpayer_id": taxpayer_id,
            "portfolio_order_id": portfolio_order_id,
            "order_type": order_type,
            "amount": amount,
            "portfolio": portfolio,
            "priority": priority,
            "timestamp": timestamp
        }

def random_execution_generator():
    while True:
        ticker = random.choice(tickers)

        taxpayer_id = random.randint(1,100) #it's 2009 all over again
        portfolio_order_id = str(uuid.uuid1())
        component_order_id = str(uuid.uuid1())
        market_order_id=str(uuid.uuid1())
        order_type = random.choice(order_types)
        symbol = ticker.symbol
        requested_amount = random.randint(10,500) # small-batch
        requested_shares = random.randint(1,100)
        requested_price = round(float(ticker.min + ticker.max) / 2, 6)
        timestamp = time.time()
        yield {
            "taxpayer_id": taxpayer_id,
            "portfolio_order_id": portfolio_order_id,
            "component_order_id": component_order_id,
            "market_order_id": market_order_id,
            "order_type": order_type,
            "symbol": symbol,
            "requested_amount": requested_amount,
            "requested_shares": requested_shares,
            "requested_price": requested_price,
            "timestamp": timestamp
        }

def random_fill_generator():
    while True:
        ticker = random.choice(tickers)
        order_type = random.choice(order_types)

        taxpayer_id = random.randint(1,100) #it's 2009 all over again
        portfolio_order_id = str(uuid.uuid1())
        component_order_id = str(uuid.uuid1())
        market_order_id=str(uuid.uuid1())
        execution_id=str(uuid.uuid1())
        fill_id=str(uuid.uuid1())
        symbol = ticker.symbol
        filled_amount = random.randint(10,500) # small-batch
        filled_shares = random.randint(1,100)
        filled_price = round(float(ticker.min + ticker.max) / 2, 6)
        delta_shares_position = filled_shares*-1 if order_type=="SELL" else filled_shares
        delta_cash_position = filled_amount*-1 if order_type=="BUY" else filled_amount
        timestamp = time.time()
        yield {
            "taxpayer_id": taxpayer_id,
            "portfolio_order_id": portfolio_order_id,
            "component_order_id": component_order_id,
            "market_order_id": market_order_id,
            "execution_id": execution_id,
            "fill_id": fill_id,
            "symbol": symbol,
            "filled_amount": filled_amount,
            "filled_shares": filled_shares,
            "filled_price": filled_price,
            "delta_shares_position": delta_shares_position,
            "delta_cash_position": delta_cash_position,
            "timestamp": timestamp
        }

@task
@retry(retry_on_exception=is_kafka_exception, stop_max_attempt_number=2)
def queue_ticks(test=False, kafka_hosts=None, topic_name='ticks', num_ticks=500):
    """Seed the local Kafka cluster's "ticks" topic with sample tick data."""
    kafka_hosts = kafka_hosts or KAFKA_HOST
    kafka = KafkaClient(kafka_hosts)
    producer = SimpleProducer(kafka)
    # 

    print("{}Seeding Kafka ({}) topic '{}' with {:,} fake ticks."
           .format(("TEST " if test else ""),kafka_hosts, topic_name, num_ticks))
    ticks = random_tick_generator()
    for i in range(num_ticks):
        tick = json.dumps(next(ticks)).encode("utf-8", "ignore")
        print(tick)
        if test is False:
            producer.send_messages(topic_name, tick)
        time.sleep(1) #sleep for one second

    print("Done.")

@task
def generate_portfolio():
    """Generate sample random portfolio data."""
    total_weight = 100
    portfolio = []
    for index, ticker in enumerate(tickers):
        if (index + 1) == len(tickers): #last
            portfolio.append(PortfolioComponent(symbol=ticker.symbol, weight=(float(total_weight) / 100)))
        else:
            rand_weight = random.randint(0,total_weight)
            total_weight -= rand_weight
            portfolio.append(PortfolioComponent(symbol=ticker.symbol, weight=(float(rand_weight) / 100)))
    print(portfolio)
    return portfolio

@task
@retry(retry_on_exception=is_kafka_exception, stop_max_attempt_number=2)
def queue_orders(test=False, kafka_hosts=None, topic_name='orders', num_orders=100):
    """Seed the local Kafka cluster's "orders" topic with sample order data."""
    kafka_hosts = kafka_hosts or KAFKA_HOST
    kafka = KafkaClient(kafka_hosts)
    producer = SimpleProducer(kafka, batch_send=True, batch_send_every_n=1,
                              batch_send_every_t=1)
    orders = random_order_generator()
    for i in range(num_orders):
        order = json.dumps(next(orders)).encode("utf-8","ignore")
        print(order)
        if test is False:
            producer.send_messages(topic_name, order)
        time.sleep(1)
    print("Done.")

@task
@retry(retry_on_exception=is_kafka_exception, stop_max_attempt_number=2)
def executions(test=False, kafka_hosts=None, topic_name='executions', num_fills=1):
    """Seed random executions"""
    kafka_hosts = kafka_hosts or KAFKA_HOST
    kafka = KafkaClient(kafka_hosts)
    producer = SimpleProducer(kafka, batch_send=True, batch_send_every_n=1,
                              batch_send_every_t=1)
    fills = random_execution_generator()
    for i in range(num_fills):
        fill = json.dumps(next(fills)).encode("utf-8","ignore")
        print(fill)
        if test is False:
            producer.send_messages(topic_name, fill)
    print("Done.")

@task
@retry(retry_on_exception=is_kafka_exception, stop_max_attempt_number=2)
def queue_fills(test=False, kafka_hosts=None, topic_name='fills', num_fills=1):
    """Seed the local Kafka cluster's "fills" topic with sample fill data."""
    kafka_hosts = kafka_hosts or KAFKA_HOST
    kafka = KafkaClient(kafka_hosts)
    producer = SimpleProducer(kafka, batch_send=True, batch_send_every_n=1,
                              batch_send_every_t=1)
    fills = random_fill_generator()
    for i in range(num_fills):
        fill = json.dumps(next(fills)).encode("utf-8","ignore")
        print(fill)
        if test is False:
            producer.send_messages(topic_name, fill)
    print("Done.")



