"""
General constant enums used in the trading platform.
"""

from enum import Enum


class Direction(Enum):
    """
    Direction of order/trade/position.
    """
    LONG = "Long"
    SHORT = "Short"
    NET = "Net"


class Offset(Enum):
    """
    Offset of order/trade.
    """
    NONE = ""
    OPEN = "Open"
    CLOSE = "Close"
    CLOSETODAY = "CloseToday"
    CLOSEYESTERDAY = "CloseYesterday"


class Status(Enum):
    """
    Order status.
    """
    SUBMITTING = "Submitting"
    NOTTRADED = "Not Traded"
    PARTTRADED = "Part Traded"
    ALLTRADED = "All Traded"
    CANCELLED = "Cancelled"
    REJECTED = "Rejected"


class Product(Enum):
    """
    Product class.
    """
    EQUITY = "Equity"
    FUTURES = "Futures"
    OPTION = "Option"
    INDEX = "Index"
    FOREX = "Forex"
    SPOT = "Spot"
    ETF = "ETF"
    BOND = "Bond"
    WARRANT = "Warrant"
    SPREAD = "Spread"
    FUND = "Fund"


class OrderType(Enum):
    """
    Order type.
    """
    LIMIT = "LIMIT"
    MARKET = "MARKET"
    STOP = "STOP"
    FAK = "FAK"
    FOK = "FOK"
    RFQ = "询价"


class OptionType(Enum):
    """
    Option type.
    """
    CALL = "Call"
    PUT = "PUT"


class Exchange(Enum):
    """
    Exchange.
    """
    # Crypto
    BINANCE = "BINANCE"
    OKX = "OKX"
    BYBIT = "BYBIT"
    DERIBIT = "DERIBIT"

    # Special Function
    LOCAL = "LOCAL"         # For local generated data


class Currency(Enum):
    """
    Currency.
    """
    USD = "USD"
    HKD = "HKD"
    CNY = "CNY"
    CAD = "CAD"


class Interval(Enum):
    """
    Interval of bar data.
    """
    MINUTE = "1m"
    HOUR = "1h"
    DAILY = "d"
    WEEKLY = "w"
    TICK = "tick"
