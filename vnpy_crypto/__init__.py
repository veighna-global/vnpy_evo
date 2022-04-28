from enum import Enum

import vnpy.trader.constant as constant


# Extract original exchange name list
exchange_names = [e.name for e in constant.Exchange]

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
    "OKEX"
])

# Generate new enum class
Exchange = Enum("Exchange", exchange_names)

# Patch the exchange enum in original framework
constant.Exchange = Exchange
