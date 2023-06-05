from enum import Enum

from vnpy.trader.constant import Exchange


# Extract original exchange name list
exchange_names = [e.name for e in Exchange]

# Add crypto currency exchanges
exchange_names.extend([
    "BINANCE",
    "BITFINEX",
    "BITSTAMP",
    "BYBIT",
    "COINBASE",
    "DERIBIT",
    "DYDX",
    "FTX",
    "GATEIO",
    "HUOBI",
    "OKX"
])

# Generate new enum class
Exchange = Enum("Exchange", zip(exchange_names, exchange_names))
