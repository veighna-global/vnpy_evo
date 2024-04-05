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
    DERIBIT = "DERIBIT"

    # Global
    OTC = "OTC"

    # Special Function
    LOCAL = "LOCAL"         # For local generated data


class TransferType(Enum):
    """
    Transfer type.
    """
    SPOT_TRADING = "spot to trading"
    TRADING_SPOT = "trading to spot"

    SPOT_LINEAR = "spot to linear"
    LINEAR_SPOT = "linear to spot"

    SPOT_INVERSE = "spot to inverse"
    INVERSE_SPOT = "inverse to spot"
