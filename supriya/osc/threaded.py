import concurrent.futures
import socketserver
import threading
import time
from collections.abc import Sequence as SequenceABC
from queue import Empty, Queue
from typing import (
    Awaitable,
    Callable,
    Dict,
    Literal,
    Optional,
    Sequence,
    Tuple,
    Union,
    cast,
)

from ..enums import BootStatus
from ..typing import FutureLike
from .messages import OscBundle, OscMessage
from .protocols import (
    HealthCheck,
    OscCallback,
    OscProtocol,
    OscProtocolAlreadyConnected,
    osc_protocol_logger,
)


class ThreadedOscProtocol(OscProtocol):

    class Server(socketserver.UDPServer):
        osc_protocol: "ThreadedOscProtocol"

        def verify_request(self, request, client_address) -> bool:
            self.osc_protocol._process_command_queue()
            return True

        def service_actions(self) -> None:
            if cast(HealthCheck, self.osc_protocol.healthcheck).active:
                self.osc_protocol._run_healthcheck()

    class Handler(socketserver.BaseRequestHandler):
        def handle(self) -> None:
            data = self.request[0]
            for callback, message in cast(
                ThreadedOscProtocol.Server, self.server
            ).osc_protocol._validate_receive(data):
                callback.procedure(
                    message, *(callback.args or ()), **(callback.kwargs or {})
                )

    ### INITIALIZER ###

    def __init__(
        self,
        *,
        name: Optional[str] = None,
        on_connect_callback: Optional[Callable] = None,
        on_disconnect_callback: Optional[Callable] = None,
        on_panic_callback: Optional[Callable] = None,
    ):
        OscProtocol.__init__(
            self,
            name=name,
            on_connect_callback=on_connect_callback,
            on_disconnect_callback=on_disconnect_callback,
            on_panic_callback=on_panic_callback,
        )
        self.boot_future: concurrent.futures.Future[bool] = concurrent.futures.Future()
        self.exit_future: concurrent.futures.Future[bool] = concurrent.futures.Future()
        self.command_queue: Queue[Tuple[Literal["add", "remove"], OscCallback]] = (
            Queue()
        )
        self.lock = threading.RLock()
        # self.osc_server = self._server_factory(self.ip_address, self.port)
        # self.osc_server_thread = threading.Thread(target=self.osc_server.serve_forever)

    ### PRIVATE METHODS ###

    def _disconnect(self, panicked: bool = False) -> None:
        super()._disconnect(panicked=panicked)
        if not self.osc_server._BaseServer__shutdown_request:
            # We set the shutdown request flag rather than call .shutdown()
            # because this is often being called from _inside_ the server
            # thread.
            self.osc_server._BaseServer__shutdown_request = True
        self._on_disconnect(
            boot_future=self.boot_future,
            exit_future=self.exit_future,
            panicked=panicked,
        )

    def _on_connect(self, boot_future: FutureLike[bool]) -> None:
        super()._on_connect(boot_future=boot_future)
        if self.on_connect_callback:
            self.on_connect_callback()

    def _on_disconnect(
        self,
        *,
        boot_future: FutureLike[bool],
        exit_future: FutureLike[bool],
        panicked: bool = False,
    ) -> None:
        super()._on_disconnect(
            boot_future=boot_future,
            exit_future=exit_future,
            panicked=panicked,
        )
        if panicked and self.on_panic_callback:
            self.on_panic_callback()
        elif not panicked and self.on_disconnect_callback:
            self.on_disconnect_callback()

    def _on_healthcheck_passed(self, message: OscMessage) -> None:
        super()._on_healthcheck_passed(message)
        if self.status == BootStatus.BOOTING:
            self._on_connect(boot_future=self.boot_future)

    def _process_command_queue(self):
        while self.command_queue.qsize():
            try:
                action, callback = self.command_queue.get()
            except Empty:
                continue
            if action == "add":
                self._add_callback(callback)
            elif action == "remove":
                self._remove_callback(callback)

    def _run_healthcheck(self):
        if self.healthcheck is None:
            return
        now = time.time()
        if now < self.healthcheck_deadline:
            return
        if self.attempts > 0:
            remaining = self.healthcheck.max_attempts - self.attempts
            osc_protocol_logger.info(
                f"[{self.ip_address}:{self.port}/{self.name or hex(id(self))}] "
                f"healthcheck failed, {remaining} attempts remaining"
            )
        new_timeout = self.healthcheck.timeout * pow(
            self.healthcheck.backoff_factor, self.attempts
        )
        self.healthcheck_deadline = now + new_timeout
        self.attempts += 1
        if self.attempts <= self.healthcheck.max_attempts:
            osc_protocol_logger.info(
                f"[{self.ip_address}:{self.port}/{self.name or hex(id(self))}] "
                "healthcheck: checking ..."
            )
            self.send(OscMessage(*self.healthcheck.request_pattern))
            return
        self._disconnect(panicked=True)

    def _server_factory(self, ip_address, port):
        server = self.Server(
            (self.ip_address, self.port), self.Handler, bind_and_activate=False
        )
        server.osc_protocol = self
        return server

    ### PUBLIC METHODS ###

    def activate_healthcheck(self) -> None:
        if self._activate_healthcheck():
            cast(HealthCheck, self.healthcheck).active = True

    def connect(
        self, ip_address: str, port: int, *, healthcheck: Optional[HealthCheck] = None
    ):
        if self.status != BootStatus.OFFLINE:
            osc_protocol_logger.info(
                f"[{self.ip_address}:{self.port}/{self.name or hex(id(self))}] "
                "already connected!"
            )
            raise OscProtocolAlreadyConnected
        osc_protocol_logger.info(
            f"[{self.ip_address}:{self.port}/{self.name or hex(id(self))}] "
            "connecting ..."
        )
        self._setup(ip_address, port, healthcheck)
        self.healthcheck_deadline = time.time()
        self.boot_future = concurrent.futures.Future()
        self.exit_future = concurrent.futures.Future()
        self.osc_server = self._server_factory(ip_address, port)
        self.osc_server_thread = threading.Thread(target=self.osc_server.serve_forever)
        self.osc_server_thread.daemon = True
        self.osc_server_thread.start()
        if not self.healthcheck:
            self._on_connect(boot_future=self.boot_future)

    def disconnect(self) -> None:
        if self.status != BootStatus.ONLINE:
            osc_protocol_logger.info(
                f"[{self.ip_address}:{self.port}/{self.name or hex(id(self))}] "
                "already disconnected!"
            )
            return
        self._disconnect()

    def register(
        self,
        pattern: Sequence[Union[str, float]],
        procedure: Callable[[OscMessage], Optional[Awaitable[None]]],
        *,
        failure_pattern: Optional[Sequence[Union[str, float]]] = None,
        once: bool = False,
        args: Optional[Tuple] = None,
        kwargs: Optional[Dict] = None,
    ) -> OscCallback:
        """
        Register a callback.
        """
        # Command queue prevents lock contention.
        self.command_queue.put(
            (
                "add",
                callback := self._register(
                    pattern,
                    procedure,
                    failure_pattern=failure_pattern,
                    once=once,
                    args=args,
                    kwargs=kwargs,
                ),
            )
        )
        return callback

    def send(self, message: Union[OscBundle, OscMessage, SequenceABC, str]) -> None:
        try:
            self.osc_server.socket.sendto(
                self._send(message),
                (self.ip_address, self.port),
            )
        except OSError:
            # print(message)
            raise

    def unregister(self, callback: OscCallback) -> None:
        """
        Unregister a callback.
        """
        # Command queue prevents lock contention.
        self.command_queue.put(("remove", callback))
