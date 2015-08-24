from collections import Counter
import collections
from influxdb import InfluxDBClient
import simplejson as json
from streamparse.bolt import Bolt
from streamparse.bolt import BatchingBolt
from .models import Fill

class FillDeserializerBolt(Bolt):
    def process(self, tup):
        # TODO load to named tuple
        msg = json.loads(tup.values[0])
        print(msg)
        taxpayer_id = msg.get("taxpayer_id")
        portfolio_order_id = msg.get("portfolio_order_id")
        component_order_id = msg.get("component_order_id")
        market_order_id = msg.get("market_order_id")
        execution_id = msg.get("execution_id")
        fill_id = msg.get("fill_id")
        symbol = msg.get("symbol")
        filled_amount = msg.get("filled_amount")
        filled_shares = msg.get("filled_shares")
        filled_price = msg.get("filled_price")
        delta_shares_position = msg.get("delta_shares_position")
        delta_cash_position = msg.get("delta_cash_position")
        timestamp = msg.get("timestamp")
        self.emit([
            taxpayer_id, 
            portfolio_order_id, 
            component_order_id, 
            market_order_id, 
            execution_id,
            fill_id,
            symbol,
            filled_amount, 
            filled_shares, 
            filled_price, 
            delta_shares_position, 
            delta_cash_position, 
            timestamp]) 

class FillInfluxDBLoaderBolt(Bolt):
    # TODO use passed in options
    # This spout may need to throttle while doing bulk inserts
    def initialize(self, storm_conf, context):
        #TODO debug storm_conf, context
        self.client = InfluxDBClient("streamparse-box", 8086, "root", "root", "prices_development")

    def process(self, tup):
        print(tup)
        fill = Fill(*tup.values)

        # tags are dimensions, fields are facts
        payload = {
            "measurement": "fills",
            "tags": {
                "taxpayer_id": str(fill.taxpayer_id),
                "portfolio_order_id": str(fill.portfolio_order_id),
                "component_order_id": str(fill.component_order_id),
                "market_order_id": str(fill.market_order_id),
                "execution_id": str(fill.execution_id),
                "fill_id": str(fill.fill_id),
                "symbol": str(fill.symbol)
            },
            "fields": {
                "filled_amount": fill.filled_amount,
                "filled_price": fill.filled_price,
                "filled_shares": fill.filled_shares,
                "delta_shares_position": fill.delta_shares_position,
                "delta_cash_position": fill.delta_cash_position
            },
            "timestamp": fill.timestamp
        }
        self.client.write_points([payload])