from enum import Enum

from vnpy.trader.constant import (
    Direction,
    Offset,
    Status,
    Product,
    OrderType,
    OptionType,
    Currency,
    Interval
)


class Exchange(Enum):
    """
    Exchange.
    """
    # Crypto
    BINANCE = "BINANCE"
    OKX = "OKX"
    BYBIT = "BYBIT"
    BTSE = "BTSE"
    DERIBIT = "DERIBIT"

    # Global
    OTC = "OTC"

    # Special Function
    LOCAL = "LOCAL"         # For local generated data
