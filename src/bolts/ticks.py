from influxdb import InfluxDBClient
import simplejson as json
from streamparse.bolt import Bolt
from .models import Tick

class TickDeserializerBolt(Bolt):
    # TODO Kafka schema can do this!
    def process(self, tup):
        # Exceptions are automatically caught and reported
        msg = json.loads(tup.values[0])
        symbol = msg.get("symbol")
        exchange = msg.get("exchange")
        bid = msg.get("bid")
        ask = msg.get("ask")
        timestamp = msg.get("timestamp")
        self.emit([symbol, exchange, bid, ask, timestamp]) # auto anchored

class InfluxDBLoaderBolt(Bolt):
    # TODO use passed in options
    # This spout may need to throttle while doing bulk inserts
    def initialize(self, storm_conf, context):
        #TODO debug storm_conf, context
        self.client = InfluxDBClient('streamparse-box', 8086, 'root', 'root', 'prices_development')

    def process(self, tup):
        tick = Tick(*tup.values)
        json_body = [
        {
            "measurement": "bid_ask",
            "tags": {
                "symbol": tup.values[0],
                "exchange": tup.values[1]
            },
            "fields": {
                "bid": tup.values[2],
                "ask": tup.values[3]
            },
            "timestamp": tup.values[4]
        }]
        self.client.write_points(json_body)
