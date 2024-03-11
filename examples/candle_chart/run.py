from datetime import datetime

from vnpy_evo.trader.ui import create_qapp, QtCore
from vnpy_evo.trader.constant import Exchange, Interval
from vnpy_evo.trader.database import get_database
from vnpy_evo.chart import ChartWidget, VolumeItem, CandleItem


if __name__ == "__main__":
    app = create_qapp()

    database = get_database()
    bars = database.load_bar_data(
        "BTCUSDT",
        Exchange.BINANCE,
        interval=Interval.MINUTE,
        start=datetime(2023, 1, 1),
        end=datetime(2023, 3, 31)
    )

    widget = ChartWidget()
    widget.add_plot("candle", hide_x_axis=True)
    widget.add_plot("volume", maximum_height=200)
    widget.add_item(CandleItem, "candle", "candle")
    widget.add_item(VolumeItem, "volume", "volume")
    widget.add_cursor()

    n = 1000
    history = bars[:n]
    new_data = bars[n:]

    widget.update_history(history)

    def update_bar():
        bar = new_data.pop(0)
        widget.update_bar(bar)

    timer = QtCore.QTimer()
    timer.timeout.connect(update_bar)
    # timer.start(100)

    widget.show()
    app.exec()
