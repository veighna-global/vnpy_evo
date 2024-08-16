from datetime import datetime
from threading import Thread
from queue import Queue, Empty

import requests
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
        self.add_engine(TelegramEngine)


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


class TelegramEngine(BaseEngine):
    """Telegram message sending engine"""

    def __init__(self, main_engine: MainEngine, event_engine: EventEngine) -> None:
        super().__init__(main_engine, event_engine, "telegram")

        self.active: bool = SETTINGS.get("telegram.active", False)
        self.token: str = SETTINGS.get("telegram.token", "")
        self.chat: str = SETTINGS.get("telegram.chat", "")
        self.url: str = f"https://api.telegram.org/bot{self.token}/sendMessage"

        self.proxies: dict[str, str] = {}
        proxy: str = SETTINGS.get("telegram.proxy", "")
        if proxy:
            self.proxies["http"] = proxy
            self.proxies["https"] = proxy

        self.thread: Thread = Thread(target=self.run, daemon=True)
        self.queue: Queue = Queue()

        if self.active:
            self.register_event()
            self.thread.start()

    def register_event(self) -> None:
        """Register event handler"""
        self.event_engine.register(EVENT_LOG, self.process_log_event)

    def process_log_event(self, event: Event) -> None:
        """Process log event"""
        log: LogData = event.data

        msg = f"{log.time}\t[{log.gateway_name}] {log.msg}"
        self.queue.put(msg)

    def close(self) -> None:
        """Stop task thread"""
        if not self.active:
            return

        self.active = False
        self.thread.join()

    def run(self) -> None:
        """Task thread loop"""
        while self.active:
            try:
                msg: str = self.queue.get(block=True, timeout=1)
                self.send_msg(msg)
            except Empty:
                pass

    def send_msg(self, msg: str) -> dict:
        """Sending message"""
        data: dict = {
            "chat_id": self.chat,
            "text": msg
        }

        # 发送请求
        try:
            r: requests.Response = requests.post(self.url, data=data)
            return r.json()
        except Exception:
            return None
