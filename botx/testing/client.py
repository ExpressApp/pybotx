"""Definition of client for testing."""
from contextlib import contextmanager
from typing import Any, Dict, Generator, List, Optional, Tuple, Type, Union

import httpx

from botx.bots.bots import Bot
from botx.clients.methods.base import BotXMethod
from botx.clients.methods.v3.command.command_result import CommandResult
from botx.clients.methods.v3.events.edit_event import EditEvent
from botx.clients.methods.v3.notification.direct_notification import NotificationDirect
from botx.clients.methods.v3.notification.notification import Notification
from botx.middlewares.exceptions import ExceptionMiddleware
from botx.models import receiving
from botx.models.messages import Message
from botx.testing.botx_mock.asgi.application import get_botx_asgi_api
from botx.testing.botx_mock.wsgi.application import get_botx_wsgi_api
from botx.testing.typing import APIMessage, APIRequest


class _ExceptionMiddleware(ExceptionMiddleware):
    """Replacement of built-in ExceptionMiddleware that will raise errors."""

    async def _handle_error_in_handler(self, exc: Exception, message: Message) -> None:
        handler = self._lookup_handler_for_exception(exc)

        if handler is None:
            raise exc

        await super()._handle_error_in_handler(exc, message)


ErrorsOverrides = Dict[Type[BotXMethod], Tuple[int, Any]]


class TestClient:
    """Test client for testing bots."""

    # https://docs.pytest.org/en/latest/changelog.html#changes
    # Allow to skip test classes from being collected
    __test__ = False

    def __init__(
        self,
        bot: Bot,
        errors: Optional[ErrorsOverrides] = None,
        suppress_errors: bool = False,
    ) -> None:
        """Init client with required query_params.

        Arguments:
            bot: bot that should be tested.
            errors: errors that should be raised from methods calls.
            suppress_errors: if True then don't raise raise errors from handlers.
        """
        self.bot: Bot = bot
        """Bot that will be patched for tests."""
        self._original_http_client = bot.client.http_client
        self._original_sync_http_client = bot.sync_client.http_client
        self._error_middleware: Optional[ExceptionMiddleware] = None
        self._messages: List[APIMessage] = []
        self._requests: List[APIRequest] = []
        self._errors = errors or {}
        self._suppress_errors = suppress_errors

    def __enter__(self) -> "TestClient":
        """Mock original HTTP client."""
        is_error_middleware = isinstance(
            self.bot.exception_middleware, ExceptionMiddleware,
        )
        if not self._suppress_errors and is_error_middleware:
            self._error_middleware = self.bot.exception_middleware
            self.bot.exception_middleware = _ExceptionMiddleware(
                self.bot.exception_middleware.executor,
            )
            self.bot.exception_middleware._exception_handlers = (
                self._error_middleware._exception_handlers
            )

        self.bot.client.http_client = httpx.AsyncClient(
            app=get_botx_asgi_api(self._messages, self._requests, self._errors),
        )
        self.bot.sync_client.http_client = httpx.Client(
            app=get_botx_wsgi_api(self._messages, self._requests, self._errors),
        )

        return self

    def __exit__(self, *_: Any) -> None:
        """Restore original HTTP client and clear storage."""
        if self._error_middleware is not None:
            self.bot.exception_middleware = self._error_middleware

        self.bot.client.http_client = self._original_http_client
        self.bot.sync_client.http_client = self._original_sync_http_client
        self._messages = []

    @contextmanager
    def error_client(
        self, errors: Dict[Type[BotXMethod], Tuple[int, Any]],
    ) -> Generator["TestClient", None, None]:
        override_errors = {**self._errors, **errors}
        with TestClient(self.bot, override_errors, self._suppress_errors) as client:
            yield client

    async def send_command(
        self, message: receiving.IncomingMessage, sync: bool = True
    ) -> None:
        """Send command message to bot.

        Arguments:
            message: message with command for bot.
            sync: if is `True` then wait while command is full executed.
        """
        await self.bot.execute_command(message.dict())

        if sync:
            await self.bot.wait_current_handlers()

    @property
    def requests(self) -> Tuple[APIRequest, ...]:
        """Return all requests that were sent by bot.

        Returns:
            Sequence of requests that were sent from bot.
        """
        return tuple(request.copy(deep=True) for request in self._requests)

    @property
    def messages(self) -> Tuple[APIMessage, ...]:
        """Return all entities that were sent by bot.

        Returns:
            Sequence of messages that were sent from bot.
        """
        return tuple(message.copy(deep=True) for message in self._messages)

    @property
    def command_results(self) -> Tuple[CommandResult, ...]:
        """Return all command results that were sent by bot.

        Returns:
            Sequence of command results that were sent from bot.
        """
        return tuple(
            message for message in self.messages if isinstance(message, CommandResult)
        )

    @property
    def notifications(self) -> Tuple[Union[Notification, NotificationDirect], ...]:
        """Return all notifications that were sent by bot.

        Returns:
            Sequence of notifications that were sent by bot.
        """
        return tuple(
            message
            for message in self.messages
            if isinstance(message, (Notification, NotificationDirect))
        )

    @property
    def message_updates(self) -> Tuple[EditEvent, ...]:
        """Return all updates that were sent by bot.

        Returns:
            Sequence of updates that were sent by bot.
        """
        return tuple(
            message for message in self.messages if isinstance(message, EditEvent)
        )
