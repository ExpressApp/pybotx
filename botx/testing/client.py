"""Definition of client for testing."""

from typing import Any, List, Optional, Tuple

import httpx

from botx import concurrency
from botx.bots.bots import Bot
from botx.middlewares.exceptions import ExceptionMiddleware
from botx.models import receiving, requests
from botx.models.messages import Message
from botx.models.requests import CommandResult, Notification, UpdatePayload
from botx.testing.botx_mock.application import get_botx_api
from botx.testing.typing import APIMessage, APIRequest


class _ExceptionMiddleware(ExceptionMiddleware):
    """Replacement of built-in ExceptionMiddleware that will raise errors."""

    async def _handle_error_in_handler(self, exc: Exception, message: Message) -> None:
        handler = self._lookup_handler_for_exception(exc)

        if handler is None:
            raise exc

        await concurrency.callable_to_coroutine(handler, exc, message)


class TestClient:  # noqa: WPS214
    """Test client for testing bots."""

    # https://docs.pytest.org/en/latest/changelog.html#changes
    # Allow to skip test classes from being collected
    __test__ = False

    def __init__(
        self, bot: Bot, generate_error_api: bool = False, suppress_errors: bool = False
    ) -> None:
        """Init client with required params.

        Arguments:
            bot: bot that should be tested.
            generate_error_api: mocked BotX API will return errored responses.
            suppress_errors: if True then don't raise raise errors from handlers.
        """
        self.bot: Bot = bot
        """Bot that will be patched for tests."""
        self._original_http_client = bot.client.http_client
        self._error_middleware: Optional[ExceptionMiddleware] = None
        self._messages: List[APIMessage] = []
        self._requests: List[APIRequest] = []
        self._generate_error_api = generate_error_api
        self._suppress_errors = suppress_errors

    @property
    def generate_error_api(self) -> bool:
        """Regenerate BotX API mock."""
        return self._generate_error_api

    @generate_error_api.setter
    def generate_error_api(self, generate_errored: bool) -> None:
        """Regenerate BotX API mock."""
        self._generate_error_api = generate_errored
        self.bot.client.http_client = httpx.AsyncClient(
            app=get_botx_api(self._messages, self._requests, self.generate_error_api)
        )

    def __enter__(self) -> "TestClient":
        """Mock original HTTP client."""
        is_error_middleware = isinstance(
            self.bot.exception_middleware, ExceptionMiddleware
        )
        if not self._suppress_errors and is_error_middleware:
            self._error_middleware = self.bot.exception_middleware
            self.bot.exception_middleware = _ExceptionMiddleware(
                self.bot.exception_middleware.executor
            )
            self.bot.exception_middleware._exception_handlers = (  # noqa: WPS437
                self._error_middleware._exception_handlers  # noqa: WPS437
            )

        self.bot.client.http_client = httpx.AsyncClient(
            app=get_botx_api(self._messages, self._requests, self.generate_error_api)
        )

        return self

    def __exit__(self, *_: Any) -> None:
        """Restore original HTTP client and clear storage."""
        if self._error_middleware is not None:
            self.bot.exception_middleware = self._error_middleware

        self.bot.client.http_client = self._original_http_client
        self._messages = []

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
            message
            for message in self.messages
            if isinstance(message, requests.CommandResult)
        )

    @property
    def notifications(self) -> Tuple[Notification, ...]:
        """Return all notifications that were sent by bot.

        Returns:
            Sequence of notifications that were sent by bot.
        """
        return tuple(
            message
            for message in self.messages
            if isinstance(message, requests.Notification)
        )

    @property
    def message_updates(self) -> Tuple[UpdatePayload, ...]:
        """Return all updates that were sent by bot.

        Returns:
            Sequence of updates that were sent by bot.
        """
        return tuple(
            message
            for message in self.messages
            if isinstance(message, requests.UpdatePayload)
        )
