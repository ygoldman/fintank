import collections

Tick = collections.namedtuple("Tick",
    ["symbol","exchange","bid","ask","timestamp"])

PortfolioOrder = collections.namedtuple("PortfolioOrder", 
    ["taxpayer_id",
    "portfolio_order_id",
    "order_type",
    "amount",
    "portfolio",
    "priority", 
    "timestamp"])

ComponentOrder = collections.namedtuple("ComponentOrder",
    ["taxpayer_id","portfolio_order_id","component_order_id","order_type","symbol","amount","priority","timestamp"])

MarketOrder = collections.namedtuple("MarketOrder",
    ["taxpayer_id","portfolio_order_id","component_order_id","market_order_id",
    "order_type","symbol",
    "requested_amount","requested_shares","requested_price",
    "timestamp"])

# Execution skipped - for demo MarketOrder==Execution - in reality Execution will have order routing info

Fill = collections.namedtuple("Fill", [
    "taxpayer_id",
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
    "timestamp"])