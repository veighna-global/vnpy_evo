from types import ModuleType
import webbrowser
from functools import partial
from importlib import import_module
from typing import Callable, Dict, List, Tuple

from qfluentwidgets import (
    FluentWindow,
    FluentIcon as FIF,
    Pivot,
    PushButton,
    RoundMenu,
    Action,
    MessageBox
)


import vnpy
from vnpy.event import EventEngine
from vnpy.trader.locale import _

from .qt import QtCore, QtGui, QtWidgets
from .widget import (
    BaseMonitor,
    TickMonitor,
    OrderMonitor,
    TradeMonitor,
    PositionMonitor,
    AccountMonitor,
    LogMonitor,
    ActiveOrderMonitor,
    ConnectDialog,
    ContractManager,
    TradingWidget,
    AboutDialog,
    GlobalDialog
)
from ..engine import MainEngine, BaseApp
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

        self.window_title: str = _("VeighNa Trader 社区版 - {}   [{}]").format(vnpy.__version__, TRADER_DIR)

        self.widgets: Dict[str, QtWidgets.QWidget] = {}
        self.monitors: Dict[str, BaseMonitor] = {}

        self.init_ui()

    def init_ui(self) -> None:
        """"""
        self.setWindowTitle(self.window_title)

        icon: QtGui.QIcon = QtGui.QIcon(get_icon_path(__file__, "veighna.ico"))
        self.setWindowIcon(icon)

        self.init_widgets()
        self.init_navigation()
        # self.init_toolbar()
        # self.init_menu()
        # self.load_window_setting("custom")

    def init_widgets(self) -> None:
        """"""
        self.home_widget = HomeWidget(self.main_engine, self.event_engine)
        self.home_widget.setObjectName("home")

        self.contract_manager = ContractManager(self.main_engine, self.event_engine)
        self.contract_manager.setObjectName("contract")

    def init_navigation(self) -> None:
        """"""
        self.addSubInterface(self.home_widget, FIF.HOME, "Home")
        self.addSubInterface(self.contract_manager, FIF.SEARCH, "Find Contract")

    def init_menu(self) -> None:
        """"""
        bar: QtWidgets.QMenuBar = self.menuBar()
        bar.setNativeMenuBar(False)     # for mac and linux

        # System menu
        sys_menu: QtWidgets.QMenu = bar.addMenu(_("系统"))

        gateway_names: list = self.main_engine.get_all_gateway_names()
        for name in gateway_names:
            func: Callable = partial(self.connect_gateway, name)
            self.add_action(
                sys_menu,
                _("连接{}").format(name),
                get_icon_path(__file__, "connect.ico"),
                func
            )

        sys_menu.addSeparator()

        self.add_action(
            sys_menu,
            _("退出"),
            get_icon_path(__file__, "exit.ico"),
            self.close
        )

        # App menu
        app_menu: QtWidgets.QMenu = bar.addMenu(_("功能"))

        all_apps: List[BaseApp] = self.main_engine.get_all_apps()
        for app in all_apps:
            ui_module: ModuleType = import_module(app.app_module + ".ui")
            widget_class: QtWidgets.QWidget = getattr(ui_module, app.widget_name)

            func: Callable = partial(self.open_widget, widget_class, app.app_name)

            self.add_action(app_menu, app.display_name, app.icon_name, func, True)

        # Global setting editor
        action: QtGui.QAction = QtWidgets.QAction(_("配置"), self)
        action.triggered.connect(self.edit_global_setting)
        bar.addAction(action)

        # Help menu
        help_menu: QtWidgets.QMenu = bar.addMenu(_("帮助"))

        self.add_action(
            help_menu,
            _("查询合约"),
            get_icon_path(__file__, "contract.ico"),
            partial(self.open_widget, ContractManager, "contract"),
            True
        )

        self.add_action(
            help_menu,
            _("还原窗口"),
            get_icon_path(__file__, "restore.ico"),
            self.restore_window_setting
        )

        self.add_action(
            help_menu,
            _("测试邮件"),
            get_icon_path(__file__, "email.ico"),
            self.send_test_email
        )

        self.add_action(
            help_menu,
            _("社区论坛"),
            get_icon_path(__file__, "forum.ico"),
            self.open_forum,
            True
        )

        self.add_action(
            help_menu,
            _("关于"),
            get_icon_path(__file__, "about.ico"),
            partial(self.open_widget, AboutDialog, "about"),
        )

    def init_toolbar(self) -> None:
        """"""
        self.toolbar: QtWidgets.QToolBar = QtWidgets.QToolBar(self)
        self.toolbar.setObjectName(_("工具栏"))
        self.toolbar.setFloatable(False)
        self.toolbar.setMovable(False)

        # Set button size
        w: int = 40
        size = QtCore.QSize(w, w)
        self.toolbar.setIconSize(size)

        # Set button spacing
        self.toolbar.layout().setSpacing(10)

        self.addToolBar(QtCore.Qt.LeftToolBarArea, self.toolbar)

    def add_action(
        self,
        menu: QtWidgets.QMenu,
        action_name: str,
        icon_name: str,
        func: Callable,
        toolbar: bool = False
    ) -> None:
        """"""
        icon: QtGui.QIcon = QtGui.QIcon(icon_name)

        action: QtGui.QAction = QtWidgets.QAction(action_name, self)
        action.triggered.connect(func)
        action.setIcon(icon)

        menu.addAction(action)

        if toolbar:
            self.toolbar.addAction(action)

    def create_dock(
        self,
        widget_class: QtWidgets.QWidget,
        name: str,
        area: int
    ) -> Tuple[QtWidgets.QWidget, QtWidgets.QDockWidget]:
        """
        Initialize a dock widget.
        """
        widget: QtWidgets.QWidget = widget_class(self.main_engine, self.event_engine)
        if isinstance(widget, BaseMonitor):
            self.monitors[name] = widget

        dock: QtWidgets.QDockWidget = QtWidgets.QDockWidget(name)
        dock.setWidget(widget)
        dock.setObjectName(name)
        dock.setFeatures(dock.DockWidgetFloatable | dock.DockWidgetMovable)
        self.addDockWidget(area, dock)
        return widget, dock

    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        """
        Call main engine close function before exit.
        """
        msgbox: MessageBox = MessageBox("Notice", "Do you confirm exit?", self.window())
        reply: int = msgbox.exec()

        if reply:
            for widget in self.widgets.values():
                widget.close()

            for monitor in self.monitors.values():
                monitor.save_setting()

            self.main_engine.close()

            event.accept()
        else:
            event.ignore()

    def open_widget(self, widget_class: QtWidgets.QWidget, name: str) -> None:
        """
        Open contract manager.
        """
        widget: QtWidgets.QWidget = self.widgets.get(name, None)
        if not widget:
            widget = widget_class(self.main_engine, self.event_engine)
            self.widgets[name] = widget

        if isinstance(widget, QtWidgets.QDialog):
            widget.exec()
        else:
            widget.show()

    def save_window_setting(self, name: str) -> None:
        """
        Save current window size and state by trader path and setting name.
        """
        settings: QtCore.QSettings = QtCore.QSettings(self.window_title, name)
        settings.setValue("state", self.saveState())
        settings.setValue("geometry", self.saveGeometry())

    def load_window_setting(self, name: str) -> None:
        """
        Load previous window size and state by trader path and setting name.
        """
        settings: QtCore.QSettings = QtCore.QSettings(self.window_title, name)
        state = settings.value("state")
        geometry = settings.value("geometry")

        if isinstance(state, QtCore.QByteArray):
            self.restoreState(state)
            self.restoreGeometry(geometry)

    def restore_window_setting(self) -> None:
        """
        Restore window to default setting.
        """
        self.load_window_setting("default")
        self.showMaximized()

    def send_test_email(self) -> None:
        """
        Sending a test email.
        """
        self.main_engine.send_email("VeighNa Trader", "testing")

    def open_forum(self) -> None:
        """
        """
        webbrowser.open("https://www.vnpy.com/forum/")

    def edit_global_setting(self) -> None:
        """
        """
        dialog: GlobalDialog = GlobalDialog()
        dialog.exec()


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

        self.menu: RoundMenu  = RoundMenu(parent=self)

        self.menu_button: PushButton = PushButton("System")
        self.menu_button.clicked.connect(self.show_menu)

        # Set layout
        mid_pivot = PivotWidgdet(self)
        mid_pivot.add_widget(self.active_monitor, "Active")
        mid_pivot.add_widget(self.order_monitor, "Order")

        bottom_pivot = PivotWidgdet(self)
        bottom_pivot.add_widget(self.log_monitor, "Log")
        bottom_pivot.add_widget(self.trade_monitor, "Trade")
        bottom_pivot.add_widget(self.position_monitor, "Position")
        bottom_pivot.add_widget(self.account_monitor, "Account")

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
        pos = self.menu_button.mapToGlobal(QtCore.QPoint(self.menu_button.width() + 5, -100))
        self.menu.exec(pos, ani=True)

    def connect_gateway(self, gateway_name: str) -> None:
        """
        Open connect dialog for gateway connection.
        """
        dialog: ConnectDialog = ConnectDialog(self.main_engine, gateway_name, self)
        dialog.exec()
