import sys
from datetime import datetime

from loguru import logger

from vnpy.trader.engine import (
    BaseEngine,
    EventEngine,
    MainEngine as OriginalMainEngine,
    OmsEngine,
    EmailEngine,
    Event,
    EVENT_LOG,
    Path,
    get_folder_path
)

from .object import LogData
from .setting import SETTINGS


class MainEngine(OriginalMainEngine):
    """New main engine of VeighNa Evo"""

    def init_engines(self) -> None:
        """
        Init all engines.
        """
        self.add_engine(LogEngine)
        self.add_engine(OmsEngine)
        self.add_engine(EmailEngine)


class LogEngine(BaseEngine):
    """Use loguru instead of logging"""

    def __init__(self, main_engine: MainEngine, event_engine: EventEngine) -> None:
        """"""
        super().__init__(main_engine, event_engine, "log")

        self.active = SETTINGS["log.active"]
        self.level: int = SETTINGS["log.level"]
        self.format: str = "{time}  {level}: {message}"

        if not SETTINGS["log.console"]:
            logger.remove()     # Remove default stderr output

        if SETTINGS["log.file"]:
            today_date: str = datetime.now().strftime("%Y%m%d")
            filename: str = f"vt_{today_date}.log"
            log_path: Path = get_folder_path("log")
            file_path: Path = log_path.joinpath(filename)

            logger.add(
                sink=file_path,
                level=self.level,
                retention="4 weeks"
            )

        self.register_event()

    def register_event(self) -> None:
        """Register log event handler"""
        self.event_engine.register(EVENT_LOG, self.process_log_event)

    def process_log_event(self, event: Event) -> None:
        """Process log event"""
        if not self.active:
            return

        log: LogData = event.data
        logger.log(log.level, log.msg)
