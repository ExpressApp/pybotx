"""Implementation for bot classes."""

import asyncio
from typing import Any, Callable, Dict, List, Optional, Sequence, Set, Type

from loguru import logger

from botx import clients, concurrency, exception_handlers, exceptions, typing, utils
from botx.bots.clients.clients import ClientsMixin
from botx.bots.collecting import BotCollectingMixin
from botx.collecting import Collector, Handler
from botx.dependencies import models as deps
from botx.exceptions import ServerUnknownError
from botx.middlewares.base import BaseMiddleware
from botx.middlewares.exceptions import ExceptionMiddleware
from botx.models import datastructures, menu, messages
from botx.models.credentials import ExpressServer


class Bot(BotCollectingMixin, ClientsMixin):  # noqa: WPS230
    """Class that implements bot behaviour."""

    def __init__(
        self,
        *,
        handlers: Optional[List[Handler]] = None,
        known_hosts: Optional[Sequence[ExpressServer]] = None,
        dependencies: Optional[Sequence[deps.Depends]] = None,
    ) -> None:
        """Init bot with required params.

        Arguments:
            handlers: list of handlers that will be stored in this bot after init.
            known_hosts: list of servers that will be used for handling message.
            dependencies: background dependencies for all handlers of bot.
        """

        self.collector: Collector = Collector(
            handlers=handlers,
            dependencies=dependencies,
            dependency_overrides_provider=self,
        )
        """collector for all handlers registered on bot."""

        self.sync_client = clients.Client()
        self.exception_middleware = ExceptionMiddleware(self.collector)

        self.client: clients.AsyncClient = clients.AsyncClient()
        """BotX API async client."""

        self.dependency_overrides: Dict[Callable, Callable] = {}
        """overrider for dependencies that can be used in tests."""

        self.known_hosts: List[ExpressServer] = utils.optional_sequence_to_list(
            known_hosts
        )
        """list of servers that will be used for handling message."""

        self.state: datastructures.State = datastructures.State()
        """state that can be used in bot for storing something."""

        self._tasks: Set[asyncio.Future] = set()

        self.add_exception_handler(
            exceptions.DependencyFailure,
            exception_handlers.dependency_failure_exception_handler,
        )
        self.add_exception_handler(
            exceptions.NoMatchFound, exception_handlers.no_match_found_exception_handler
        )

    async def status(self) -> menu.Status:
        """Generate status object that could be return to BotX API on `/status`."""
        status = menu.Status()
        for handler in self.handlers:
            if callable(handler.include_in_status):
                include_in_status = await concurrency.callable_to_coroutine(
                    handler.include_in_status
                )
            else:
                include_in_status = handler.include_in_status

            if include_in_status:
                status.result.commands.append(
                    menu.MenuCommand(
                        description=handler.description or "",
                        body=handler.body,
                        name=handler.name,
                    )
                )

        return status

    async def execute_command(self, message: dict) -> None:
        """Process data with incoming message and handle command inside.

        Arguments:
            message: incoming message to bot.

        Raises:
            ServerUnknownError: raised if message was received from unregistered host.
        """
        logger.bind(botx_bot=True, payload=message).debug("process incoming message")
        msg = messages.Message.from_dict(message, self)
        for server in self.known_hosts:
            if server.host == msg.host:
                await self(msg)
                break
        else:
            raise ServerUnknownError(host=msg.host)

    def add_middleware(
        self, middleware_class: Type[BaseMiddleware], **kwargs: Any
    ) -> None:
        """Register new middleware for execution before handler.

        Arguments:
            middleware_class: middleware that should be registered.
            kwargs: arguments that are required for middleware initialization.
        """
        self.exception_middleware.executor = middleware_class(
            self.exception_middleware.executor, **kwargs
        )

    def middleware(self, handler: typing.Executor) -> Callable:  # noqa: D202
        """Register callable as middleware for request.

        Arguments:
            handler: handler for middleware logic.

        Returns:
            Passed `handler` callable.
        """

        self.add_middleware(BaseMiddleware, dispatch=handler)
        return handler

    def add_exception_handler(
        self, exc_class: Type[Exception], handler: typing.ExceptionHandler
    ) -> None:
        """Register new handler for exception.

        Arguments:
            exc_class: exception type that should be handled.
            handler: handler for exception.
        """
        self.exception_middleware.add_exception_handler(exc_class, handler)

    def exception_handler(self, exc_class: Type[Exception]) -> Callable:  # noqa: D202
        """Register callable as handler for exception.

        Arguments:
            exc_class: exception type that should be handled.

        Returns:
            Decorator that will register exception and return passed function.
        """

        def decorator(handler: typing.ExceptionHandler) -> Callable:
            self.add_exception_handler(exc_class, handler)
            return handler

        return decorator

    async def shutdown(self) -> None:
        """Wait for all running handlers shutdown."""
        if self._tasks:
            await asyncio.wait(self._tasks, return_when=asyncio.ALL_COMPLETED)

        self._tasks = set()

    async def __call__(self, message: messages.Message) -> None:
        """Iterate through collector, find handler and execute it, running middlewares.

        Arguments:
            message: message that will be proceed by handler.
        """
        self._tasks.add(asyncio.ensure_future(self.exception_middleware(message)))
