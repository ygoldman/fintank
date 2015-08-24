from collections import Counter
import collections
from influxdb import InfluxDBClient
import simplejson as json
from streamparse.bolt import Bolt
from streamparse.bolt import BatchingBolt
import uuid
from .models import PortfolioOrder, ComponentOrder, MarketOrder


class PortfolioOrderDeserializerBolt(Bolt):
    def process(self, tup):
        # TODO load to named tuple
        msg = json.loads(tup.values[0])
        taxpayer_id = msg.get("taxpayer_id")
        portfolio_order_id = msg.get("portfolio_order_id")
        order_type = msg.get("order_type")
        amount = msg.get("amount")
        portfolio = msg.get("portfolio")
        priority = msg.get("priority")
        timestamp = msg.get("timestamp")
        self.emit([
            taxpayer_id, 
            portfolio_order_id, 
            order_type, 
            amount, 
            portfolio, 
            priority, 
            timestamp]) # auto anchored    

class MarketOrderDeserializerBolt(Bolt):
    def process(self, tup):
        # TODO load to named tuple
        msg = json.loads(tup.values[0])
        taxpayer_id = msg.get("taxpayer_id")
        portfolio_order_id = msg.get("portfolio_order_id")
        component_order_id = msg.get("component_order_id")
        market_order_id = msg.get("market_order_id")
        order_type = msg.get("order_type")
        symbol = msg.get("symbol")
        requested_amount = msg.get("requested_amount")
        requested_shares = msg.get("requested_shares")
        requested_price = msg.get("requested_price")
        timestamp = msg.get("timestamp")
        self.emit([taxpayer_id, portfolio_order_id, component_order_id, market_order_id,
            order_type, symbol,
            requested_amount, requested_shares, requested_price, timestamp]) # auto anchored    

class PortfolioOrderInfluxDBLoaderBolt(Bolt):
    # TODO use passed in options
    # This spout may need to throttle while doing bulk inserts
    def initialize(self, storm_conf, context):
        #TODO debug storm_conf, context
        self.client = InfluxDBClient("streamparse-box", 8086, "root", "root", "prices_development")

    def process(self, tup):
        print("-----")
        print(tup.values)
        order = PortfolioOrder(*tup.values)
        print(order)
        # tags are dimensions, fields are facts
        payload = {
            "measurement": "portfolio_orders",
            "tags": {
                "taxpayer_id": str(order.taxpayer_id),
                "portfolio_order_id": str(order.portfolio_order_id),
                "order_type": str(order.order_type)
            },
            "fields": {
                "amount": order.amount,
                "priority": order.priority
            },
            "timestamp": order.timestamp
        }
        #portfolio = json.loads(tup.values[4])
        # add portfolio components to tags
        #for component in portfolio:
        #    tag_name = "portfolio_component_"+component.get("symbol")
        #    tag_value = component.get("weight")
        #    portfolio_order.get("tags").update({tag_name:tag_value})
        #print(payload)
        self.client.write_points([payload])

class ComponentOrderCreatorBolt(Bolt):
    """ takes in a single Portfolio order and emits multiple Component orders """
    def process(self, tup):
        order = PortfolioOrder(*tup.values)
        component_orders = [ (order.taxpayer_id
                             ,order.portfolio_order_id
                             ,str(uuid.uuid1()) #component_order_id
                             ,order.order_type
                             ,component.get("symbol")
                             ,round(order.amount * float(component.get("weight")), 6)
                             ,order.priority
                             ,order.timestamp) 
                            for component in order.portfolio ]
        print(component_orders)

        # TODO: does streamparse support multiple streams?
        # stream = "priority1" if order.priority == 1 else "default"
        self.emit_many(component_orders)

class ComponentOrderInfluxDBLoaderBolt(Bolt):
    def initialize(self, storm_conf, context):
        self.client = InfluxDBClient("streamparse-box", 8086, "root", "root", "prices_development")

    def process(self, tup):
        order = ComponentOrder(*tup.values)
        print(order)
        # tags are dimensions, fields are facts
        payload = {
            "measurement": "portfolio_component_orders",
            "tags": {
                "taxpayer_id": str(order.taxpayer_id),
                "portfolio_order_id": str(order.portfolio_order_id),
                "component_order_id": str(order.component_order_id),
                "order_type": str(order.order_type),
                "symbol": str(order.symbol)
            },
            "fields": {
                "amount": order.amount,
                "priority": order.priority
            },
            "timestamp": order.timestamp
        }
        self.client.write_points([payload])
 

class ComponentOrderAggregatorBolt(BatchingBolt):

    def initialize(self, conf, ctx):
        self.totals = Counter()

    def group_key(self, tup):
        order = ComponentOrder(*tup.values)
        return order.symbol

    def process_batch(self, key, tups):
        orders = [ ComponentOrder(*tup) for tup in tups ]
        self.totals[key] += sum(order.amount for order in orders)
        self.emit([key, self.totals[key]])
