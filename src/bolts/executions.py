from collections import Counter
import collections
from influxdb import InfluxDBClient
import simplejson as json
from streamparse.bolt import Bolt
from streamparse.bolt import BatchingBolt
from kafka.common import UnknownTopicOrPartitionError
from kafka.client import KafkaClient
from kafka.producer import SimpleProducer
from .models import Tick, PortfolioOrder, ComponentOrder, MarketOrder, Fill
import time
import uuid

KAFKA_HOST="streamparse-box:9092"
MARKET_EXECUTION_TOPIC="executions"
MARKET_FILL_TOPIC="fills"

# TODO refactor to orders.py
class Order:
    @staticmethod
    def to_market_order(component_order, price_tick):
        price = float(price_tick.bid) if component_order.order_type == "BUY" else float(price_tick.ask)
        market_order = MarketOrder(
                taxpayer_id=component_order.taxpayer_id
                ,portfolio_order_id=component_order.portfolio_order_id
                ,component_order_id=component_order.component_order_id
                ,market_order_id=str(uuid.uuid1())
                ,order_type=component_order.order_type
                ,symbol=component_order.symbol
                ,requested_amount=component_order.amount
                ,requested_shares=round(float(component_order.amount) / price,6)
                ,requested_price=price
                ,timestamp=time.time()
            )
        return market_order

    @staticmethod
    def to_fake_fill(market_order, execution_id):
        fill = Fill(
                taxpayer_id=market_order.taxpayer_id
                ,portfolio_order_id=market_order.portfolio_order_id
                ,component_order_id=market_order.component_order_id
                ,market_order_id=market_order.market_order_id
                ,execution_id=execution_id
                ,fill_id=str(uuid.uuid1())
                ,symbol=market_order.symbol
                ,filled_amount=market_order.requested_amount
                ,filled_shares=market_order.requested_shares
                ,filled_price=market_order.requested_price
                ,delta_shares_position=market_order.requested_shares*-1 if market_order.order_type=="SELL" else market_order.requested_shares 
                ,delta_cash_position=market_order.requested_amount*-1 if market_order.order_type=="BUY" else market_order.requested_amount
                ,timestamp=time.time()
            )
        return fill

class OrderPrioritizationBolt(Bolt):
    symbol_ticks = {}

    def initialize(self, storm_conf, context):
        kafka = KafkaClient(KAFKA_HOST)
        self.queue = SimpleProducer(kafka, batch_send=True, batch_send_every_n=1,
            batch_send_every_t=1) # batching config can be tuned

    def process(self, tup):
        if self.__is_price_tick(tup):
            tick = Tick(*tup.values)
            self.__update_tick_by_symbol(tick)
        elif self.__is_component_order(tup):
            component_order = ComponentOrder(*tup.values)
            if component_order.priority == 1:
                # execute the order
                self.queue_execution(component_order)
            else:
                # pass lower priority orders on
                self.emit(list(component_order))
        else:
            raise TypeError("Unrecognized tuple {}".format(tup))

    def queue_execution(self, component_order):
        # FIXEME we assume that latest price exists
        latest_price_tick = self.symbol_ticks[component_order.symbol]
        market_order = Order.to_market_order(component_order, latest_price_tick)
        payload = json.dumps(market_order._asdict()).encode("utf-8","ignore")
        self.queue.send_messages(MARKET_EXECUTION_TOPIC, payload)

    def __is_price_tick(self, tup):
        return True if tup.component.startswith("tick") else False

    def __is_component_order(self, tup):
        return True if tup.component.startswith("component-order") else False

    def __update_tick_by_symbol(self, tick):
        self.symbol_ticks[tick.symbol] = tick


class FakeExecuteMarketOrderBolt(Bolt):

    def initialize(self, storm_conf, context):
        #TODO debug storm_conf, context
        self.client = InfluxDBClient("streamparse-box", 8086, "root", "root", "prices_development")
        kafka = KafkaClient(KAFKA_HOST)
        self.queue = SimpleProducer(kafka, batch_send=True, batch_send_every_n=1,
            batch_send_every_t=1) # batching config can be tuned


    # TODO this can be a BatchBolt for interesting last-opportunity aggregation of orders, maybe?
    def process(self, tup):
        market_order = MarketOrder(*tup.values)
        # FAKE MARKET ORDER
        print("MARKET ORDER EXECUTED: {}".format(market_order))
        execution_id = str(uuid.uuid1())

        # load to timeseries!
        self.save_execution(market_order, execution_id)

        # Fake process a Fill, put on fills queue
        fill = Order.to_fake_fill(market_order, execution_id)
        self.queue_fill(fill)

    def queue_fill(self, fill):
        payload = json.dumps(fill._asdict()).encode("utf-8","ignore")
        self.queue.send_messages(MARKET_FILL_TOPIC, payload)

    def save_execution(self, market_order, execution_id):
        payload = {
            "measurement": "executions",
            "tags": {
                "taxpayer_id": str(market_order.taxpayer_id),
                "portfolio_order_id": str(market_order.portfolio_order_id),
                "component_order_id": str(market_order.component_order_id),
                "market_order_id": str(market_order.market_order_id),
                "execution_id": execution_id,
                "order_type": str(market_order.order_type),
                "symbol": str(market_order.symbol)
            },
            "fields": {
                "requested_amount": market_order.requested_amount,
                "requested_price": market_order.requested_price,
                "requested_shares": market_order.requested_shares
            },
            "timestamp": market_order.timestamp
        }
        self.client.write_points([payload])
