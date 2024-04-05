from dataclasses import dataclass

from vnpy.trader.object import *

from .constant import TransferType


@dataclass
class TransferRequest:
    """
    Request sending to specific gateway for transferring fund.
    """

    asset: str
    volume: int
    type: TransferType


@dataclass
class TransferData:
    """
    Transfer data contains information for tracking lastest status
    of a specific transfer.
    """

    transferid: str
    asset: str
    volume: int
    type: TransferType
