from types import ModuleType
import webbrowser
from functools import partial
from importlib import import_module

from typing import Callable, Type

from qfluentwidgets import (
    FluentWindow, MessageBox,
    FluentIcon as FIF,
    PushButton, RoundMenu,
    Action, NavigationItemPosition,
)

from vnpy.event import EventEngine

import vnpy_evo
from .qt import QtCore, QtGui, QtWidgets
from .widget import (
    ConnectDialog,
    TradingWidget,
    AboutDialog,
    GlobalDialog,
    PivotWidgdet
)
from .monitor import (
    TickMonitor,
    OrderMonitor,
    TradeMonitor,
    PositionMonitor,
    AccountMonitor,
    LogMonitor,
    ActiveOrderMonitor,
    ContractManager
)
from ..app import BaseApp
from ..engine import MainEngine
from ..utility import get_icon_path, TRADER_DIR


class MainWindow(FluentWindow):
    """
    Main window of the trading platform.
    """

    def __init__(self, main_engine: MainEngine, event_engine: EventEngine) -> None:
        """"""
        super().__init__()

        self.main_engine: MainEngine = main_engine
        self.event_engine: EventEngine = event_engine

        self.window_title: str = f"VeighNa Evo - {vnpy_evo.__version__}  [{TRADER_DIR}]"

        self.app_widgets: dict[str, QtWidgets.QWidget] = {}

        self.init_ui()

    def init_ui(self) -> None:
        """"""
        self.setWindowTitle(self.window_title)

        icon: QtGui.QIcon = QtGui.QIcon(get_icon_path(__file__, "veighna.ico"))
        self.setWindowIcon(icon)

        self.init_widgets()
        self.init_navigation()

    def init_widgets(self) -> None:
        """"""
        self.home_widget = HomeWidget(self.main_engine, self.event_engine)
        self.home_widget.setObjectName("home")

        self.contract_manager = ContractManager(self.main_engine, self.event_engine)
        self.contract_manager.setObjectName("contract")

        all_apps: list[BaseApp] = self.main_engine.get_all_apps()
        for app in all_apps:
            ui_module: ModuleType = import_module(app.app_module + ".ui")
            widget_class: Type = getattr(ui_module, app.widget_name)
            widget: QtWidgets.QWidget = widget_class(self.main_engine, self.event_engine)
            widget.setObjectName(app.display_name)
            self.app_widgets[app.display_name] = widget

    def init_navigation(self) -> None:
        """"""
        self.addSubInterface(self.home_widget, FIF.HOME, "Home")
        self.addSubInterface(self.contract_manager, FIF.SEARCH, "Find contract")

        for name, widget in self.app_widgets.items():
            self.addSubInterface(widget, FIF.ROBOT, name)

        self.navigationInterface.addItem(
            routeKey="froum",
            icon=FIF.HELP,
            text="Community forum",
            onClick=self.open_forum,
            selectable=False,
            position=NavigationItemPosition.BOTTOM
        )

        self.navigationInterface.addItem(
            routeKey="github",
            icon=FIF.GITHUB,
            text="Github",
            onClick=self.open_github,
            selectable=False,
            position=NavigationItemPosition.BOTTOM
        )

        self.navigationInterface.addItem(
            routeKey="setting",
            icon=FIF.SETTING,
            text="Settings",
            onClick=self.edit_global_setting,
            selectable=False,
            position=NavigationItemPosition.BOTTOM
        )

        self.navigationInterface.addItem(
            routeKey="about",
            icon=FIF.INFO,
            text="About",
            onClick=self.open_about,
            selectable=False,
            position=NavigationItemPosition.BOTTOM
        )

    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        """
        Call main engine close function before exit.
        """
        msgbox: MessageBox = MessageBox("Notice", "Do you confirm exit?", self.window())
        reply: int = msgbox.exec()

        if reply:
            self.main_engine.close()

            event.accept()
        else:
            event.ignore()

    def open_forum(self) -> None:
        """
        """
        webbrowser.open("https://www.vnpy.com/forum/")

    def open_github(self) -> None:
        """
        """
        webbrowser.open("https://github.com/veighna-global/vnpy_evo")

    def edit_global_setting(self) -> None:
        """
        """
        dialog: GlobalDialog = GlobalDialog(self)
        dialog.exec()

    def open_about(self) -> None:
        """
        Open contract manager.
        """
        dialog: AboutDialog = AboutDialog(self)
        dialog.exec()


class HomeWidget(QtWidgets.QWidget):
    """"""

    def __init__(self, main_engine: MainEngine, event_engine: EventEngine) -> None:
        """"""
        super().__init__()

        self.main_engine: MainEngine = main_engine
        self.event_engine: EventEngine = event_engine

        self.init_ui()
        self.init_menu()

    def init_ui(self) -> None:
        """"""
        # Create widgets
        self.trading_widget = TradingWidget(self.main_engine, self.event_engine)
        self.tick_monitor = TickMonitor(self.main_engine, self.event_engine)
        self.order_monitor = OrderMonitor(self.main_engine, self.event_engine)
        self.active_monitor = ActiveOrderMonitor(self.main_engine, self.event_engine)
        self.trade_monitor = TradeMonitor(self.main_engine, self.event_engine)
        self.position_monitor = PositionMonitor(self.main_engine, self.event_engine)
        self.account_monitor = AccountMonitor(self.main_engine, self.event_engine)
        self.log_monitor = LogMonitor(self.main_engine, self.event_engine)

        self.menu: RoundMenu = RoundMenu(parent=self)

        self.menu_button: PushButton = PushButton("Connect Gateway")
        self.menu_button.clicked.connect(self.show_menu)

        # Set layout
        mid_pivot = PivotWidgdet(self)
        mid_pivot.add_widget(self.active_monitor, "Open Orders")
        mid_pivot.add_widget(self.order_monitor, "Order History")

        bottom_pivot = PivotWidgdet(self)
        bottom_pivot.add_widget(self.log_monitor, "Log")
        bottom_pivot.add_widget(self.trade_monitor, "Trade History")
        bottom_pivot.add_widget(self.position_monitor, "Positions")
        bottom_pivot.add_widget(self.account_monitor, "Assets")

        vbox1 = QtWidgets.QVBoxLayout()
        vbox1.addWidget(self.tick_monitor)
        vbox1.addWidget(mid_pivot)
        vbox1.addWidget(bottom_pivot)

        vbox2 = QtWidgets.QVBoxLayout()
        vbox2.addWidget(self.trading_widget)
        vbox2.addWidget(self.menu_button)

        hbox = QtWidgets.QHBoxLayout()
        hbox.addLayout(vbox2)
        hbox.addLayout(vbox1)

        self.setLayout(hbox)

        # Connect signal
        self.tick_monitor.itemDoubleClicked.connect(self.trading_widget.update_with_cell)
        self.position_monitor.itemDoubleClicked.connect(self.trading_widget.update_with_cell)

    def init_menu(self) -> None:
        """"""
        gateway_names: list = self.main_engine.get_all_gateway_names()
        for name in gateway_names:
            func: Callable = partial(self.connect_gateway, name)

            action = Action(f"Connect {name}")
            action.triggered.connect(func)

            self.menu.addAction(action)

    def show_menu(self) -> None:
        """"""
        pos = self.menu_button.mapToGlobal(QtCore.QPoint(self.menu_button.width() + 5, 0))
        self.menu.exec(pos, ani=True)

    def connect_gateway(self, gateway_name: str) -> None:
        """
        Open connect dialog for gateway connection.
        """
        dialog: ConnectDialog = ConnectDialog(self.main_engine, gateway_name, self)
        dialog.exec()
