"""Base for testing client for bots."""
from __future__ import annotations

from contextlib import contextmanager
from typing import Any, Dict, Generator, List, Optional, Tuple, Type

import httpx

from botx.bots.bots import Bot
from botx.clients.methods.base import BotXMethod
from botx.middlewares.exceptions import ExceptionMiddleware
from botx.models.messages.incoming_message import IncomingMessage
from botx.models.messages.message import Message
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


class BaseTestClient:
    """Base for testing client for bots."""

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
        self._original_http_client = bot.client.http_client
        self._original_sync_http_client = bot.sync_client.http_client
        self._error_middleware: Optional[ExceptionMiddleware] = None
        self._messages: List[APIMessage] = []
        self._requests: List[APIRequest] = []
        self._errors = errors or {}
        self._suppress_errors = suppress_errors

    def __enter__(self) -> BaseTestClient:
        """Mock original HTTP clients."""
        is_error_middleware = isinstance(
            self.bot.exception_middleware, ExceptionMiddleware,
        )
        if not self._suppress_errors and is_error_middleware:
            self._error_middleware = self.bot.exception_middleware
            self.bot.exception_middleware = _ExceptionMiddleware(
                self.bot.exception_middleware.executor,
            )
            self.bot.exception_middleware._exception_handlers = (  # noqa: WPS437
                self._error_middleware._exception_handlers  # noqa: WPS437
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
    ) -> Generator[BaseTestClient, None, None]:
        """Enter into new test client that adds error responses to mocks.

        Arguments:
            errors: overrides for errors in context.

        Yields:
            New client with overridden errors.
        """
        override_errors = {**self._errors, **errors}
        with self.__class__(self.bot, override_errors, self._suppress_errors) as client:
            yield client

    async def send_command(self, message: IncomingMessage, sync: bool = True) -> None:
        """Send command message to bot.

        Arguments:
            message: message with command for bot.
            sync: if is `True` then wait while command is full executed.
        """
        await self.bot.execute_command(message.dict())

        if sync:
            await self.bot.wait_current_handlers()
