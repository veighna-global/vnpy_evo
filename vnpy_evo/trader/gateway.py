from vnpy.trader.gateway import BaseGateway as BaseGateway_

from .object import TransferRequest, TransferData


class BaseGateway(BaseGateway_):
    """Add extra functions for standard gateway"""

    def transfer_asset(self, req: TransferRequest) -> TransferData:
        """
        Send a asset transfer request to server.
        """
        pass
