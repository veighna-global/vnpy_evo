import json
import logging
import socket
import ssl
import sys
import traceback
from datetime import datetime
from threading import Lock, Thread
from time import sleep
from typing import Optional
from types import TracebackType

import websocket

from vnpy.trader.utility import get_file_logger

import websocket.websocket_client


class WebsocketClient:
    """
    Websocket API

    After creating the client object, use start() to run worker and ping threads.
    The worker thread connects websocket automatically.

    Use stop to stop threads and disconnect websocket before destroying the client
    object (especially when exiting the programme).

    Default serialization format is json.

    Callbacks to overrides:
    * unpack_data
    * on_connected
    * on_disconnected
    * on_packet
    * on_error

    After start() is called, the ping thread will ping server every 60 seconds.

    If you want to send anything other than JSON, override send_packet.
    """

    def __init__(self) -> None:
        """Constructor"""
        self.host: str = ""

        self._ws_lock: Lock = Lock()
        self._ws: websocket.WebSocket = None

        self._worker_thread: Thread = None
        self._ping_thread: Thread = None
        self._active: bool = False

        self.proxy_host: str = ""
        self.proxy_port: int = 0
        self.ping_interval: int = 60  # seconds
        self.header: dict = {}

        self._receive_timeout: int = 0

        self.logger: Optional[logging.Logger] = None

        # For debugging
        self._last_sent_text: str = None
        self._last_received_text: str = None

    def init(
        self,
        host: str,
        proxy_host: str = "",
        proxy_port: int = 0,
        ping_interval: int = 60,
        header: dict = None,
        log_path: Optional[str] = None,
        receive_timeout: int = 60
    ) -> None:
        """
        :param host:
        :param proxy_host:
        :param proxy_port:
        :param header:
        :param ping_interval: unit: seconds, type: int
        :param log_path: optional. file to save log.
        """
        self.host = host
        self.ping_interval = ping_interval  # seconds
        if log_path is not None:
            self.logger = get_file_logger(log_path)
            self.logger.setLevel(logging.DEBUG)

        if header:
            self.header = header

        if proxy_host and proxy_port:
            self.proxy_host = proxy_host
            self.proxy_port = proxy_port

        self._receive_timeout = receive_timeout

    def start(self) -> None:
        """
        Start the client and on_connected function is called after webscoket
        is connected succesfully.

        Please don't send packet untill on_connected fucntion is called.
        """

        self._active = True
        self._worker_thread = Thread(target=self._run)
        self._worker_thread.start()

        self._ping_thread = Thread(target=self._run_ping)
        self._ping_thread.start()

    def stop(self) -> None:
        """
        Stop the client.
        """
        self._active = False
        self._disconnect()

    def join(self) -> None:
        """
        Wait till all threads finish.

        This function cannot be called from worker thread or callback function.
        """
        self._ping_thread.join()
        self._worker_thread.join()

    def send_packet(self, packet: dict) -> None:
        """
        Send a packet (dict data) to server

        override this if you want to send non-json packet
        """
        text: str = json.dumps(packet)
        self._record_last_sent_text(text)
        return self._send_text(text)

    def _log(self, msg, *args) -> None:
        """"""
        if self.logger:
            self.logger.debug(msg, *args)

    def _send_text(self, text: str) -> None:
        """
        Send a text string to server.
        """
        if self._ws:
            self._ws.send(text, opcode=websocket.ABNF.OPCODE_TEXT)
            self._log('sent text: %s', text)

    def _send_binary(self, data: bytes) -> None:
        """
        Send bytes data to server.
        """
        if self._ws:
            self._ws._send_binary(data)
            self._log('sent binary: %s', data)

    def _create_connection(self, *args, **kwargs) -> websocket.WebSocket:
        """"""
        return websocket.create_connection(timeout=self._receive_timeout, *args, **kwargs)

    def _ensure_connection(self) -> None:
        """"""
        triggered: bool = False

        with self._ws_lock:
            if self._ws is None:
                self._ws = self._create_connection(
                    self.host,
                    sslopt={"cert_reqs": ssl.CERT_NONE},
                    http_proxy_host=self.proxy_host,
                    http_proxy_port=self.proxy_port,
                    header=self.header
                )
                triggered = True

        if triggered:
            self.on_connected()

    def _disconnect(self) -> None:
        """"""
        triggered: bool = False

        with self._ws_lock:
            if self._ws:
                ws: websocket.WebSocket = self._ws
                self._ws = None

                triggered = True

        if triggered:
            ws.close()
            self.on_disconnected()

    def _run(self) -> None:
        """
        Keep running till stop is called.
        """
        try:
            while self._active:
                try:
                    self._ensure_connection()
                    ws: websocket.WebSocket = self._ws
                    if ws:
                        text: str = ws.recv()

                        # ws object is closed when recv function is blocking
                        if not text:
                            self._disconnect()
                            continue

                        self._record_last_received_text(text)

                        try:
                            data: dict = self.unpack_data(text)
                        except ValueError as e:
                            print("websocket unable to parse data: " + text)
                            raise e

                        self._log('recv data: %s', data)
                        self.on_packet(data)
                # ws is closed before recv function is called
                # For socket.error, see Issue #1608
                except (
                    websocket.WebSocketConnectionClosedException,
                    websocket.WebSocketBadStatusException,
                    socket.error
                ):
                    self._disconnect()

                # other internal exception raised in on_packet
                except:  # noqa
                    et, ev, tb = sys.exc_info()
                    self.on_error(et, ev, tb)
                    self._disconnect()
        except:  # noqa
            et, ev, tb = sys.exc_info()
            self.on_error(et, ev, tb)
        self._disconnect()

    def unpack_data(self, data: str) -> dict:
        """
        Default serialization format is json.

        override this method if you want to use other serialization format.
        """
        return json.loads(data)

    def _run_ping(self) -> None:
        """"""
        while self._active:
            try:
                self._ping()
            except:  # noqa
                et, ev, tb = sys.exc_info()
                self.on_error(et, ev, tb)

                # self._run() will reconnect websocket
                sleep(1)

            for i in range(self.ping_interval):
                if not self._active:
                    break
                sleep(1)

    def _ping(self) -> None:
        """"""
        ws = self._ws
        if ws:
            ws.send("ping", websocket.ABNF.OPCODE_PING)

    def on_connected(self) -> None:
        """
        Callback when websocket is connected successfully.
        """
        pass

    def on_disconnected(self) -> None:
        """
        Callback when websocket connection is lost.
        """
        pass

    def on_packet(packet: dict) -> None:
        """
        Callback when receiving data from server.
        """
        pass

    def on_error(self, exception_type: type, exception_value: Exception, tb) -> None:
        """
        Callback when exception raised.
        """
        sys.stderr.write(self.exception_detail(exception_type, exception_value, tb))
        return sys.excepthook(exception_type, exception_value, tb)

    def exception_detail(self, exception_type: type, exception_value: Exception, tb: TracebackType) -> str:
        """
        Print detailed exception information.
        """
        text: str = "[{}]: Unhandled WebSocket Error:{}\n".format(
            datetime.now().isoformat(), exception_type
        )
        text += "LastSentText:\n{}\n".format(self._last_sent_text)
        text += "LastReceivedText:\n{}\n".format(self._last_received_text)
        text += "Exception trace: \n"
        text += "".join(
            traceback.format_exception(exception_type, exception_value, tb)
        )
        return text

    def _record_last_sent_text(self, text: str) -> None:
        """
        Record last sent text for debug purpose.
        """
        self._last_sent_text = text[:1000]

    def _record_last_received_text(self, text: str) -> None:
        """
        Record last received text for debug purpose.
        """
        self._last_received_text = text[:1000]
