from vnpy.trader.utility import *

from .constant import Exchange


def extract_vt_symbol(vt_symbol: str) -> tuple[str, Exchange]:
    """
    return (symbol, exchange)
    """
    symbol, exchange_str = vt_symbol.rsplit(".", 1)
    return symbol, Exchange(exchange_str)
