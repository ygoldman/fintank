(ns fintank
  (:use [backtype.storm.clojure]
        [fintank.spouts.tick_spout :only [spout] :rename {spout tick-spout}]
        [fintank.spouts.order_spout :only [spout] :rename {spout order-spout}]
        [fintank.spouts.execution_spout :only [spout] :rename {spout execution-spout}]
        [fintank.spouts.fill_spout :only [spout] :rename {spout fill-spout}]
        [streamparse.specs])
  (:gen-class))


(defn fintank [options]
   [
    ;; spout configurations
    {
      "tick-spout" (spout-spec tick-spout :p 1) ;; p=parallelism
      "order-spout" (spout-spec order-spout :p 1)
      "execution-spout" (spout-spec execution-spout :p 1)
      "fill-spout" (spout-spec fill-spout :p 1)
    }

    ;; bolt configurations
    {
      ;; TODO: add a proper deserializer to Kafka spout
      "tick-deserializer" (python-bolt-spec
        options
        {"tick-spout" :shuffle}
        "bolts.ticks.TickDeserializerBolt"
        ["symbol" "exchange" "bid" "ask" "timestamp"]
        :p 1
      )

      "tick-influxdb-loader" (python-bolt-spec
        options
        ;; fields grouping on symbol
        {"tick-deserializer" :shuffle}
        "bolts.ticks.InfluxDBLoaderBolt"
        ;; terminal bolt
        []
        ;; paralelism
        :p 1
        ;; use tick tuples
        ;;:conf {"topology.tick.tuple.freq.secs", 1})
      )

      "portfolio-order-deserializer" (python-bolt-spec
        options
        {"order-spout" :shuffle}
        "bolts.orders.PortfolioOrderDeserializerBolt"
        ["taxpayer_id",
        "portfolio_order_id",
        "order_type",
        "amount",
        "portfolio",
        "priority",
        "timestamp"]
        :p 1
      )

      "portfolio-order-influxdb-loader" (python-bolt-spec
        options
        {"portfolio-order-deserializer" :shuffle}
        "bolts.orders.PortfolioOrderInfluxDBLoaderBolt"
        []
        :p 1        
      )

      "component-order-creator" (python-bolt-spec
        options
        {"portfolio-order-deserializer" :shuffle}
        "bolts.orders.ComponentOrderCreatorBolt"
        ["taxpayer_id","portfolio_order_id","component_order_id","order_type","symbol","amount","priority","timestamp"]
        :p 1 ;; :p 2
      )

      "component-order-influxdb-loader" (python-bolt-spec
        options
        {"component-order-creator" :shuffle}
        "bolts.orders.ComponentOrderInfluxDBLoaderBolt"
        []
        :p 1
      )

      "order-prioritizer" (python-bolt-spec
        options
        {
          "component-order-creator" ["symbol"] 
          "tick-deserializer" ["symbol"]
        }
        "bolts.executions.OrderPrioritizationBolt"
        ["taxpayer_id","portfolio_order_id","component_order_id","order_type","symbol","amount","priority","timestamp"]
        :p 3
      )

      "market-order-aka-execution-deserializer" (python-bolt-spec
        options
        {"execution-spout" :shuffle}
        "bolts.orders.MarketOrderDeserializerBolt"
        ["taxpayer_id","portfolio_order_id","component_order_id","market_order_id",
          "order_type","symbol",
          "requested_amount","requested_shares","requested_price",
          "timestamp"]
        :p 3
      )      
      
      "market-order-executor" (python-bolt-spec
        options
        {"market-order-aka-execution-deserializer" ["symbol"]}
        "bolts.executions.FakeExecuteMarketOrderBolt"
        [] ;;this queues fills
        :p 3
      ) 

      "fill-deserializer" (python-bolt-spec
        options
        {"fill-spout" :shuffle}
        "bolts.fills.FillDeserializerBolt"
        ["taxpayer_id",
          "portfolio_order_id",
          "component_order_id",
          "market_order_id",
          "execution_id",
          "fill_id",
          "symbol",
          "filled_amount",
          "filled_shares",
          "filled_price",
          "delta_shares_position",
          "delta_cash_position",
          "timestamp"]
        :p 3
      ) 

      "fill-influxdb-loader" (python-bolt-spec
        options
        {"fill-deserializer" :shuffle}
        "bolts.fills.FillInfluxDBLoaderBolt"
        []
        :p 1
      )
    }
  ]
)
