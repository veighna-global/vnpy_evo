from vnpy_crypto.event import EventEngine
from vnpy_crypto.trader.engine import MainEngine
from vnpy_crypto.trader.ui import MainWindow, create_qapp

from vnpy_rpcservice import RpcGateway
from vnpy_ctastrategy import CtaStrategyApp


def main():
    """"""
    qapp = create_qapp()

    event_engine = EventEngine()

    main_engine = MainEngine(event_engine)

    main_engine.add_gateway(RpcGateway)
    main_engine.add_app(CtaStrategyApp)

    main_window = MainWindow(main_engine, event_engine)
    main_window.showMaximized()

    qapp.exec()


if __name__ == "__main__":
    main()
