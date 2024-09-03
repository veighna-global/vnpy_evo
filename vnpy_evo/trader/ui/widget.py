"""
Basic widgets for UI.
"""

import platform
from copy import copy
from typing import TYPE_CHECKING

import importlib_metadata
from qfluentwidgets import (
    Pivot, MessageBoxBase, BodyLabel, SubtitleLabel,
    PushButton, ComboBox, LineEdit, CheckBox,
)

from vnpy.trader.locale import _
from .qt import QtCore, QtGui, QtWidgets
from ..constant import Direction, Exchange, Offset, OrderType
from ..engine import MainEngine, Event, EventEngine
from ..event import EVENT_TICK
from ..object import (
    OrderRequest,
    SubscribeRequest,
    CancelRequest,
    ContractData,
    PositionData,
    OrderData,
    TickData
)
from ..utility import load_json, save_json, get_digits
from ..setting import SETTING_FILENAME, SETTINGS

if TYPE_CHECKING:
    from .monitor import BaseCell


class ConnectDialog(MessageBoxBase):
    """
    Start connection of a certain gateway.
    """

    def __init__(self, main_engine: MainEngine, gateway_name: str, parent: QtWidgets.QWidget = None) -> None:
        """"""
        super().__init__(parent)

        self.main_engine: MainEngine = main_engine
        self.gateway_name: str = gateway_name
        self.filename: str = f"connect_{gateway_name.lower()}.json"

        self.widgets: dict[str, QtWidgets.QWidget] = {}

        self.init_ui()

    def init_ui(self) -> None:
        """"""
        self.title_label = SubtitleLabel(f"Connect {self.gateway_name}", self)

        # Default setting provides field name, field data type and field default value.
        default_setting: dict = self.main_engine.get_default_setting(
            self.gateway_name)

        # Saved setting provides field data used last time.
        loaded_setting: dict = load_json(self.filename)

        # Initialize line edits and form layout based on setting.
        grid: QtWidgets.QGridLayout = QtWidgets.QGridLayout()
        row: int = 0

        for field_name, field_value in default_setting.items():
            field_type: type = type(field_value)

            if field_type == list:
                widget: ComboBox = ComboBox()
                widget.addItems(field_value)

                if field_name in loaded_setting:
                    saved_value = loaded_setting[field_name]
                    ix: int = widget.findText(saved_value)
                    widget.setCurrentIndex(ix)
            else:
                widget: LineEdit = LineEdit()
                widget.setText(str(field_value))

                if field_name in loaded_setting:
                    saved_value = loaded_setting[field_name]
                    widget.setText(str(saved_value))

                if _("密码") in field_name:
                    widget.setEchoMode(LineEdit.Password)

                if field_type == int:
                    validator: QtGui.QIntValidator = QtGui.QIntValidator()
                    widget.setValidator(validator)

            grid.addWidget(BodyLabel(f"{field_name} <{field_type.__name__}>"), row, 0)
            grid.addWidget(widget, row, 1)
            self.widgets[field_name] = (widget, field_type)

            row += 1

        self.viewLayout.addWidget(self.title_label)
        self.viewLayout.addLayout(grid)

        self.yesButton.setText("Connect")
        self.yesButton.clicked.connect(self.connect_gateway)

        self.cancelButton.setText("Cancel")

        self.widget.setFixedWidth(self.widget.width() * 6)

    def connect_gateway(self) -> None:
        """
        Get setting value from line edits and connect the gateway.
        """
        setting: dict = {}
        for field_name, tp in self.widgets.items():
            widget, field_type = tp
            if field_type == list:
                field_value = str(widget.currentText())
            else:
                try:
                    field_value = field_type(widget.text())
                except ValueError:
                    field_value = field_type()
            setting[field_name] = field_value

        save_json(self.filename, setting)

        self.main_engine.connect(setting, self.gateway_name)
        self.accept()


class TradingWidget(QtWidgets.QWidget):
    """
    General manual trading widget.
    """

    signal_tick: QtCore.Signal = QtCore.Signal(Event)

    def __init__(self, main_engine: MainEngine, event_engine: EventEngine) -> None:
        """"""
        super().__init__()

        self.main_engine: MainEngine = main_engine
        self.event_engine: EventEngine = event_engine

        self.vt_symbol: str = ""
        self.price_digits: int = 0

        self.init_ui()
        self.register_event()

    def init_ui(self) -> None:
        """"""
        self.setFixedWidth(300)

        # Trading function area
        exchanges: list[Exchange] = self.main_engine.get_all_exchanges()
        self.exchange_combo: ComboBox = ComboBox()
        self.exchange_combo.addItems([exchange.value for exchange in exchanges])

        self.symbol_line: LineEdit = LineEdit()
        self.symbol_line.returnPressed.connect(self.set_vt_symbol)

        self.name_line: LineEdit = LineEdit()
        self.name_line.setReadOnly(True)

        self.direction_combo: ComboBox = ComboBox()
        self.direction_combo.addItems([Direction.LONG.value, Direction.SHORT.value])

        self.offset_combo: ComboBox = ComboBox()
        self.offset_combo.addItems([offset.value for offset in Offset])

        self.order_type_combo: ComboBox = ComboBox()
        self.order_type_combo.addItems([order_type.value for order_type in OrderType])

        double_validator: QtGui.QDoubleValidator = QtGui.QDoubleValidator()
        double_validator.setBottom(0)

        self.price_line: LineEdit = LineEdit()
        self.price_line.setValidator(double_validator)

        self.volume_line: LineEdit = LineEdit()
        self.volume_line.setValidator(double_validator)

        self.gateway_combo: ComboBox = ComboBox()
        self.gateway_combo.addItems(self.main_engine.get_all_gateway_names())

        self.price_check: CheckBox = CheckBox()
        self.price_check.setToolTip(_("设置价格随行情更新"))

        send_button: PushButton = PushButton("Send Order")
        send_button.clicked.connect(self.send_order)

        cancel_button: PushButton = PushButton("Cancel All")
        cancel_button.clicked.connect(self.cancel_all)

        grid: QtWidgets.QGridLayout = QtWidgets.QGridLayout()
        grid.addWidget(BodyLabel(_("交易所")), 0, 0)
        grid.addWidget(BodyLabel(_("代码")), 1, 0)
        grid.addWidget(BodyLabel(_("名称")), 2, 0)
        grid.addWidget(BodyLabel(_("方向")), 3, 0)
        grid.addWidget(BodyLabel(_("开平")), 4, 0)
        grid.addWidget(BodyLabel(_("类型")), 5, 0)
        grid.addWidget(BodyLabel(_("价格")), 6, 0)
        grid.addWidget(BodyLabel(_("数量")), 7, 0)
        grid.addWidget(BodyLabel(_("接口")), 8, 0)
        grid.addWidget(self.exchange_combo, 0, 1, 1, 2)
        grid.addWidget(self.symbol_line, 1, 1, 1, 2)
        grid.addWidget(self.name_line, 2, 1, 1, 2)
        grid.addWidget(self.direction_combo, 3, 1, 1, 2)
        grid.addWidget(self.offset_combo, 4, 1, 1, 2)
        grid.addWidget(self.order_type_combo, 5, 1, 1, 2)
        grid.addWidget(self.price_line, 6, 1, 1, 1)
        grid.addWidget(self.price_check, 6, 2, 1, 1)
        grid.addWidget(self.volume_line, 7, 1, 1, 2)
        grid.addWidget(self.gateway_combo, 8, 1, 1, 2)
        grid.addWidget(send_button, 9, 0, 1, 3)
        grid.addWidget(cancel_button, 10, 0, 1, 3)

        # Market depth display area
        bid_color: str = "red"
        ask_color: str = "green"

        self.bp1_label: BodyLabel = self.create_label(bid_color)
        self.bp2_label: BodyLabel = self.create_label(bid_color)
        self.bp3_label: BodyLabel = self.create_label(bid_color)
        self.bp4_label: BodyLabel = self.create_label(bid_color)
        self.bp5_label: BodyLabel = self.create_label(bid_color)

        self.bv1_label: BodyLabel = self.create_label(
            bid_color, alignment=QtCore.Qt.AlignRight)
        self.bv2_label: BodyLabel = self.create_label(
            bid_color, alignment=QtCore.Qt.AlignRight)
        self.bv3_label: BodyLabel = self.create_label(
            bid_color, alignment=QtCore.Qt.AlignRight)
        self.bv4_label: BodyLabel = self.create_label(
            bid_color, alignment=QtCore.Qt.AlignRight)
        self.bv5_label: BodyLabel = self.create_label(
            bid_color, alignment=QtCore.Qt.AlignRight)

        self.ap1_label: BodyLabel = self.create_label(ask_color)
        self.ap2_label: BodyLabel = self.create_label(ask_color)
        self.ap3_label: BodyLabel = self.create_label(ask_color)
        self.ap4_label: BodyLabel = self.create_label(ask_color)
        self.ap5_label: BodyLabel = self.create_label(ask_color)

        self.av1_label: BodyLabel = self.create_label(
            ask_color, alignment=QtCore.Qt.AlignRight)
        self.av2_label: BodyLabel = self.create_label(
            ask_color, alignment=QtCore.Qt.AlignRight)
        self.av3_label: BodyLabel = self.create_label(
            ask_color, alignment=QtCore.Qt.AlignRight)
        self.av4_label: BodyLabel = self.create_label(
            ask_color, alignment=QtCore.Qt.AlignRight)
        self.av5_label: BodyLabel = self.create_label(
            ask_color, alignment=QtCore.Qt.AlignRight)

        self.lp_label: BodyLabel = self.create_label()
        self.return_label: BodyLabel = self.create_label(alignment=QtCore.Qt.AlignRight)

        form: QtWidgets.QFormLayout = QtWidgets.QFormLayout()
        form.addRow(self.ap5_label, self.av5_label)
        form.addRow(self.ap4_label, self.av4_label)
        form.addRow(self.ap3_label, self.av3_label)
        form.addRow(self.ap2_label, self.av2_label)
        form.addRow(self.ap1_label, self.av1_label)
        form.addRow(self.lp_label, self.return_label)
        form.addRow(self.bp1_label, self.bv1_label)
        form.addRow(self.bp2_label, self.bv2_label)
        form.addRow(self.bp3_label, self.bv3_label)
        form.addRow(self.bp4_label, self.bv4_label)
        form.addRow(self.bp5_label, self.bv5_label)

        # Overall layout
        vbox: QtWidgets.QVBoxLayout = QtWidgets.QVBoxLayout()
        vbox.addLayout(grid)
        vbox.addLayout(form)
        self.setLayout(vbox)

    def create_label(
        self,
        color: str = "",
        alignment: int = QtCore.Qt.AlignLeft
    ) -> BodyLabel:
        """
        Create label with certain font color.
        """
        label: BodyLabel = BodyLabel()
        if color:
            label.setStyleSheet(f"color:{color}")
        label.setAlignment(alignment)
        return label

    def register_event(self) -> None:
        """"""
        self.signal_tick.connect(self.process_tick_event)
        self.event_engine.register(EVENT_TICK, self.signal_tick.emit)

    def process_tick_event(self, event: Event) -> None:
        """"""
        tick: TickData = event.data
        if tick.vt_symbol != self.vt_symbol:
            return

        price_digits: int = self.price_digits

        self.lp_label.setText(f"{tick.last_price:.{price_digits}f}")
        self.bp1_label.setText(f"{tick.bid_price_1:.{price_digits}f}")
        self.bv1_label.setText(str(tick.bid_volume_1))
        self.ap1_label.setText(f"{tick.ask_price_1:.{price_digits}f}")
        self.av1_label.setText(str(tick.ask_volume_1))

        if tick.pre_close:
            r: float = (tick.last_price / tick.pre_close - 1) * 100
            self.return_label.setText(f"{r:.2f}%")

        if tick.bid_price_2:
            self.bp2_label.setText(f"{tick.bid_price_2:.{price_digits}f}")
            self.bv2_label.setText(str(tick.bid_volume_2))
            self.ap2_label.setText(f"{tick.ask_price_2:.{price_digits}f}")
            self.av2_label.setText(str(tick.ask_volume_2))

            self.bp3_label.setText(f"{tick.bid_price_3:.{price_digits}f}")
            self.bv3_label.setText(str(tick.bid_volume_3))
            self.ap3_label.setText(f"{tick.ask_price_3:.{price_digits}f}")
            self.av3_label.setText(str(tick.ask_volume_3))

            self.bp4_label.setText(f"{tick.bid_price_4:.{price_digits}f}")
            self.bv4_label.setText(str(tick.bid_volume_4))
            self.ap4_label.setText(f"{tick.ask_price_4:.{price_digits}f}")
            self.av4_label.setText(str(tick.ask_volume_4))

            self.bp5_label.setText(f"{tick.bid_price_5:.{price_digits}f}")
            self.bv5_label.setText(str(tick.bid_volume_5))
            self.ap5_label.setText(f"{tick.ask_price_5:.{price_digits}f}")
            self.av5_label.setText(str(tick.ask_volume_5))

        if self.price_check.isChecked():
            self.price_line.setText(f"{tick.last_price:.{price_digits}f}")

    def set_vt_symbol(self) -> None:
        """
        Set the tick depth data to monitor by vt_symbol.
        """
        symbol: str = str(self.symbol_line.text())
        if not symbol:
            return

        # Generate vt_symbol from symbol and exchange
        exchange_value: str = str(self.exchange_combo.currentText())
        vt_symbol: str = f"{symbol}.{exchange_value}"

        if vt_symbol == self.vt_symbol:
            return
        self.vt_symbol = vt_symbol

        # Update name line widget and clear all labels
        contract: ContractData = self.main_engine.get_contract(vt_symbol)
        if not contract:
            self.name_line.setText("")
            gateway_name: str = self.gateway_combo.currentText()
        else:
            self.name_line.setText(contract.name)
            gateway_name: str = contract.gateway_name

            # Update gateway combo box.
            ix: int = self.gateway_combo.findText(gateway_name)
            self.gateway_combo.setCurrentIndex(ix)

            # Update price digits
            self.price_digits = get_digits(contract.pricetick)

        self.clear_label_text()
        self.volume_line.setText("")
        self.price_line.setText("")

        # Subscribe tick data
        req: SubscribeRequest = SubscribeRequest(
            symbol=symbol, exchange=Exchange(exchange_value)
        )

        self.main_engine.subscribe(req, gateway_name)

    def clear_label_text(self) -> None:
        """
        Clear text on all labels.
        """
        self.lp_label.setText("")
        self.return_label.setText("")

        self.bv1_label.setText("")
        self.bv2_label.setText("")
        self.bv3_label.setText("")
        self.bv4_label.setText("")
        self.bv5_label.setText("")

        self.av1_label.setText("")
        self.av2_label.setText("")
        self.av3_label.setText("")
        self.av4_label.setText("")
        self.av5_label.setText("")

        self.bp1_label.setText("")
        self.bp2_label.setText("")
        self.bp3_label.setText("")
        self.bp4_label.setText("")
        self.bp5_label.setText("")

        self.ap1_label.setText("")
        self.ap2_label.setText("")
        self.ap3_label.setText("")
        self.ap4_label.setText("")
        self.ap5_label.setText("")

    def send_order(self) -> None:
        """
        Send new order manually.
        """
        symbol: str = str(self.symbol_line.text())
        if not symbol:
            QtWidgets.QMessageBox.critical(self, _("委托失败"), _("请输入合约代码"))
            return

        volume_text: str = str(self.volume_line.text())
        if not volume_text:
            QtWidgets.QMessageBox.critical(self, _("委托失败"), _("请输入委托数量"))
            return
        volume: float = float(volume_text)

        price_text: str = str(self.price_line.text())
        if not price_text:
            price = 0
        else:
            price = float(price_text)

        req: OrderRequest = OrderRequest(
            symbol=symbol,
            exchange=Exchange(str(self.exchange_combo.currentText())),
            direction=Direction(str(self.direction_combo.currentText())),
            type=OrderType(str(self.order_type_combo.currentText())),
            volume=volume,
            price=price,
            offset=Offset(str(self.offset_combo.currentText())),
            reference="ManualTrading"
        )

        gateway_name: str = str(self.gateway_combo.currentText())

        self.main_engine.send_order(req, gateway_name)

    def cancel_all(self) -> None:
        """
        Cancel all active orders.
        """
        order_list: list[OrderData] = self.main_engine.get_all_active_orders()
        for order in order_list:
            req: CancelRequest = order.create_cancel_request()
            self.main_engine.cancel_order(req, order.gateway_name)

    def update_with_cell(self, cell: "BaseCell") -> None:
        """"""
        data = cell.get_data()

        self.symbol_line.setText(data.symbol)
        self.exchange_combo.setCurrentIndex(
            self.exchange_combo.findText(data.exchange.value)
        )

        self.set_vt_symbol()

        if isinstance(data, PositionData):
            if data.direction == Direction.SHORT:
                direction: Direction = Direction.LONG
            elif data.direction == Direction.LONG:
                direction: Direction = Direction.SHORT
            else:       # Net position mode
                if data.volume > 0:
                    direction: Direction = Direction.SHORT
                else:
                    direction: Direction = Direction.LONG

            self.direction_combo.setCurrentIndex(
                self.direction_combo.findText(direction.value)
            )
            self.offset_combo.setCurrentIndex(
                self.offset_combo.findText(Offset.CLOSE.value)
            )
            self.volume_line.setText(str(abs(data.volume)))


class AboutDialog(MessageBoxBase):
    """
    Information about the trading platform.
    """

    def __init__(self, parent: QtWidgets.QWidget) -> None:
        """"""
        super().__init__(parent)

        self.init_ui()

    def init_ui(self) -> None:
        """"""
        self.title_label = SubtitleLabel("About VeighNa Evo", self)

        from vnpy import __version__ as vnpy_version
        from ... import __version__ as evo_version

        text: str = f"""
            By Traders, For Traders.

            Created by VeighNa Technology


            License：MIT
            Website：www.vnpy.com
            Github：www.github.com/vnpy/vnpy


            VeighNa Evo - {evo_version}
            VeighNa - {vnpy_version}
            Python - {platform.python_version()}
            PySide6 - {importlib_metadata.version("pyside6")}
            NumPy - {importlib_metadata.version("numpy")}
            pandas - {importlib_metadata.version("pandas")}
            """

        label: BodyLabel = BodyLabel()
        label.setText(text)
        label.setMinimumWidth(500)

        self.viewLayout.addWidget(self.title_label)
        self.viewLayout.addWidget(label)

        self.cancelButton.hide()


class GlobalDialog(MessageBoxBase):
    """
    Edit global setting.
    """

    def __init__(self, parent: QtWidgets.QWidget = None) -> None:
        """"""
        super().__init__(parent)

        self.widgets: dict[str, object] = {}

        self.init_ui()

    def init_ui(self) -> None:
        """"""
        self.title_label = SubtitleLabel("Global Configuration", self)

        settings: dict = copy(SETTINGS)
        settings.update(load_json(SETTING_FILENAME))

        # Initialize line edits and form layout based on setting.
        scroll_widget: QtWidgets.QWidget = QtWidgets.QWidget(parent=self)

        grid: QtWidgets.QFormLayout = QtWidgets.QGridLayout(parent=scroll_widget)
        row: int = 0

        for field_name, field_value in settings.items():
            if "datafeed" in field_name:
                continue

            field_type: type = type(field_value)
            widget: LineEdit = LineEdit()
            widget.setText(str(field_value))

            grid.addWidget(BodyLabel(f"{field_name} <{field_type.__name__}>"), row, 0)
            grid.addWidget(widget, row, 1)
            self.widgets[field_name] = (widget, field_type)

            row += 1

        scroll_widget.setLayout(grid)

        self.viewLayout.addWidget(self.title_label)
        self.viewLayout.addWidget(scroll_widget)

        self.yesButton.setText("Confirm")
        self.yesButton.clicked.connect(self.update_setting)

        self.widget.setFixedWidth(self.widget.width() * 6)

    def update_setting(self) -> None:
        """
        Get setting value from line edits and update global setting file.
        """
        settings: dict = {}
        for field_name, tp in self.widgets.items():
            widget, field_type = tp
            value_text: str = widget.text()

            if field_type == bool:
                if value_text == "True":
                    field_value: bool = True
                else:
                    field_value: bool = False
            else:
                field_value = field_type(value_text)

            settings[field_name] = field_value

        QtWidgets.QMessageBox.information(
            self,
            _("注意"),
            _("全局配置的修改需要重启后才会生效！"),
            QtWidgets.QMessageBox.Ok
        )

        save_json(SETTING_FILENAME, settings)
        self.accept()


class PivotWidgdet(QtWidgets.QWidget):
    """"""

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.pivot = Pivot(self)
        self.stacked_widget = QtWidgets.QStackedWidget(self)
        self.vbox = QtWidgets.QVBoxLayout(self)

        self.vbox.addWidget(self.pivot, 0, QtCore.Qt.AlignLeft)
        self.vbox.addWidget(self.stacked_widget)
        self.vbox.setContentsMargins(0, 0, 0, 0)

        self.stacked_widget.currentChanged.connect(self.onCurrentIndexChanged)

    def add_widget(self, widget: QtWidgets.QWidget, name: str) -> None:
        """"""
        widget.setObjectName(name)

        self.stacked_widget.addWidget(widget)

        self.pivot.addItem(
            routeKey=name,
            text=name,
            onClick=lambda: self.stacked_widget.setCurrentWidget(widget)
        )

        if self.stacked_widget.count() == 1:
            self.stacked_widget.setCurrentWidget(widget)
            self.pivot.setCurrentItem(widget.objectName())

    def onCurrentIndexChanged(self, index: int) -> None:
        """"""
        widget: QtWidgets.QWidget = self.stacked_widget.widget(index)
        self.pivot.setCurrentItem(widget.objectName())
