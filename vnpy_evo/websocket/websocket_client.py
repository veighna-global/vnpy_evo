import json
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
        self.active: bool = False
        self.host: str = ""

        self.ws_lock: Lock = Lock()
        self.ws: websocket.WebSocket = None

        self.worker_thread: Thread = None
        self.ping_thread: Thread = None

        self.proxy_host: Optional[str] = None
        self.proxy_port: Optional[int] = None
        self.header: Optional[dict] = None
        self.ping_interval: int = 0
        self.receive_timeout: int = 0

        self.last_sent_text: str = ""
        self.last_received_text: str = ""

    def init(
        self,
        host: str,
        proxy_host: str = "",
        proxy_port: int = 0,
        ping_interval: int = 10,
        receive_timeout: int = 60,
        header: dict = None,
    ) -> None:
        """
        :param host:
        :param proxy_host:
        :param proxy_port:
        :param header:
        :param ping_interval: unit: seconds, type: int
        """
        self.host = host
        self.ping_interval = ping_interval  # seconds
        self.receive_timeout = receive_timeout

        if header:
            self.header = header

        if proxy_host and proxy_port:
            self.proxy_host = proxy_host
            self.proxy_port = proxy_port

    def start(self) -> None:
        """
        Start the client and on_connected function is called after webscoket
        is connected succesfully.

        Please don't send packet untill on_connected fucntion is called.
        """
        self.active = True
        self.worker_thread = Thread(target=self.run)
        self.worker_thread.start()

        self.ping_thread = Thread(target=self.run_ping)
        self.ping_thread.start()

    def stop(self) -> None:
        """
        Stop the client.
        """
        self.active = False
        self.disconnect()

    def join(self) -> None:
        """
        Wait till all threads finish.

        This function cannot be called from worker thread or callback function.
        """
        self.ping_thread.join()
        self.worker_thread.join()

    def send_packet(self, packet: dict) -> None:
        """
        Send a packet (dict data) to server

        override this if you want to send non-json packet
        """
        text: str = json.dumps(packet)
        self.record_last_sent_text(text)
        self.ws.send(text, opcode=websocket.ABNF.OPCODE_TEXT)

    def unpack_data(self, data: str) -> dict:
        """
        Default serialization format is json.

        override this method if you want to use other serialization format.
        """
        return json.loads(data)

    def create_connection(self, *args, **kwargs) -> websocket.WebSocket:
        """"""
        return websocket.create_connection(timeout=self.receive_timeout, *args, **kwargs)

    def ensure_connection(self) -> None:
        """"""
        triggered: bool = False

        with self.ws_lock:
            if self.ws is None:
                self.ws = self.create_connection(
                    self.host,
                    sslopt={"cert_reqs": ssl.CERT_NONE},
                    http_proxy_host=self.proxy_host,
                    http_proxy_port=self.proxy_port,
                    header=self.header
                )
                triggered = True

        if triggered:
            self.on_connected()

    def disconnect(self) -> None:
        """"""
        triggered: bool = False

        with self.ws_lock:
            if self.ws:
                ws: websocket.WebSocket = self.ws
                self.ws = None

                triggered = True

        if triggered:
            ws.close()
            self.on_disconnected()

    def run(self) -> None:
        """
        Keep running till stop is called.
        """
        try:
            while self.active:
                try:
                    self.ensure_connection()
                    ws: websocket.WebSocket = self.ws
                    if ws:
                        text: str = ws.recv()

                        # ws object is closed when recv function is blocking
                        if not text:
                            self.disconnect()
                            continue

                        self.record_last_received_text(text)

                        try:
                            data: dict = self.unpack_data(text)
                        except ValueError as e:
                            print("websocket unable to parse data: " + text)
                            raise e

                        self.on_packet(data)
                # ws is closed before recv function is called
                # For socket.error, see Issue #1608
                except (
                    websocket.WebSocketConnectionClosedException,
                    websocket.WebSocketBadStatusException,
                    socket.error
                ):
                    self.disconnect()

                # other internal exception raised in on_packet
                except:  # noqa
                    et, ev, tb = sys.exc_info()
                    self.on_error(et, ev, tb)
                    self.disconnect()
        except:  # noqa
            et, ev, tb = sys.exc_info()
            self.on_error(et, ev, tb)
        self.disconnect()

    def run_ping(self) -> None:
        """"""
        while self.active:
            try:
                self.ping()
            except:  # noqa
                et, ev, tb = sys.exc_info()
                self.on_error(et, ev, tb)

                # self.run() will reconnect websocket
                sleep(1)

            for i in range(self.ping_interval):
                if not self.active:
                    break
                sleep(1)

    def ping(self) -> None:
        """"""
        ws = self.ws
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
        try:
            print("WebsocketClient on error" + "-" * 10)
            print(self.exception_detail(exception_type, exception_value, tb))
        except Exception:
            traceback.print_exc()

    def exception_detail(
        self,
        exception_type: type,
        exception_value: Exception,
        tb: TracebackType
    ) -> str:
        """
        Print detailed exception information.
        """
        text: str = "[{}]: Unhandled WebSocket Error:{}\n".format(
            datetime.now().isoformat(), exception_type
        )
        text += "LastSentText:\n{}\n".format(self.last_sent_text)
        text += "LastReceivedText:\n{}\n".format(self.last_received_text)
        text += "Exception trace: \n"
        text += "".join(
            traceback.format_exception(exception_type, exception_value, tb)
        )
        return text

    def _record_last_sent_text(self, text: str) -> None:
        """
        Record last sent text for debug purpose.
        """
        self.last_sent_text = text[:1000]

    def _record_last_received_text(self, text: str) -> None:
        """
        Record last received text for debug purpose.
        """
        self.last_received_text = text[:1000]
