"""Implementation for bot classes."""

import asyncio
from dataclasses import InitVar, field
from typing import Any, Callable, Dict, List
from weakref import WeakSet

from loguru import logger
from pydantic.dataclasses import dataclass

from botx import concurrency, exception_handlers, exceptions, shared, typing
from botx.bots.mixins import (
    clients,
    collectors,
    exceptions as exception_mixin,
    lifespan,
    middlewares,
)
from botx.clients.clients import async_client, sync_client as synchronous_client
from botx.collecting.collectors.collector import Collector
from botx.dependencies.models import Depends
from botx.middlewares.authorization import AuthorizationMiddleware
from botx.middlewares.exceptions import ExceptionMiddleware
from botx.models import credentials, datastructures, menu
from botx.models.messages.message import Message


@dataclass(config=shared.BotXDataclassConfig)
class Bot(  # noqa: WPS215
    collectors.BotCollectingMixin,
    clients.ClientsMixin,
    lifespan.LifespanMixin,
    middlewares.MiddlewareMixin,
    exception_mixin.ExceptionHandlersMixin,
):
    """Class that implements bot behaviour."""

    dependencies: InitVar[List[Depends]] = field(default=None)
    bot_accounts: List[credentials.BotXCredentials] = field(default_factory=list)
    startup_events: List[typing.BotLifespanEvent] = field(default_factory=list)
    shutdown_events: List[typing.BotLifespanEvent] = field(default_factory=list)

    client: async_client.AsyncClient = field(init=False)
    sync_client: synchronous_client.Client = field(init=False)
    collector: Collector = field(init=False)
    exception_middleware: ExceptionMiddleware = field(init=False)
    state: datastructures.State = field(init=False)
    dependency_overrides: Dict[Callable, Callable] = field(
        init=False,
        default_factory=dict,
    )

    tasks: WeakSet = field(init=False, default_factory=WeakSet)

    async def __call__(self, message: Message) -> None:
        """Iterate through collector, find handler and execute it, running middlewares.

        Arguments:
            message: message that will be proceed by handler.
        """
        self.tasks.add(asyncio.ensure_future(self.exception_middleware(message)))

    def __post_init__(self, dependencies: List[Depends]) -> None:
        """Initialize special fields.

        Arguments:
            dependencies: initial background dependencies for inner collector.
        """
        self.state = datastructures.State()
        self.client = async_client.AsyncClient()
        self.sync_client = synchronous_client.Client()
        self.collector = Collector(
            dependencies=dependencies,
            dependency_overrides_provider=self,
        )
        self.exception_middleware = ExceptionMiddleware(self.collector)

        self.add_exception_handler(
            exceptions.DependencyFailure,
            exception_handlers.dependency_failure_exception_handler,
        )
        self.add_exception_handler(
            exceptions.NoMatchFound,
            exception_handlers.no_match_found_exception_handler,
        )
        self.add_middleware(AuthorizationMiddleware)

    async def status(self, *args: Any, **kwargs: Any) -> menu.Status:
        """Generate status object that could be return to BotX API on `/status`.

        Arguments:
            args: additional positional arguments that will be passed to callable
                status function.
            kwargs: additional key arguments that will be passed to callable
                status function.

        Returns:
            Built status for returning to BotX API.
        """
        status = menu.Status()
        for handler in self.handlers:
            if callable(handler.include_in_status):
                include_in_status = await concurrency.callable_to_coroutine(
                    handler.include_in_status,
                    *args,
                    **kwargs,
                )
            else:
                include_in_status = handler.include_in_status

            if include_in_status:
                status.result.commands.append(
                    menu.MenuCommand(
                        description=handler.description or "",
                        body=handler.body,
                        name=handler.name,
                    ),
                )

        return status

    async def execute_command(self, message: dict) -> None:
        """Process data with incoming message and handle command inside.

        Arguments:
            message: incoming message to bot.
        """
        logger.bind(botx_bot=True, payload=message).debug("process incoming message")
        msg = Message.from_dict(message, self)

        # raise UnknownBotError if not registered.
        self.get_account_by_bot_id(msg.bot_id)

        await self(msg)

    async def authorize(self, *args: Any) -> None:
        """Process auth for each bot account."""
        for account in self.bot_accounts:
            try:
                token = await self.get_token(
                    account.host,
                    account.bot_id,
                    account.signature,
                )
            except (exceptions.BotXAPIError, exceptions.BotXConnectError) as exc:
                logger.bind(botx_bot=True).warning(
                    f"Credentials `host - {account.host}, "  # noqa: WPS305
                    f"bot_id - {account.bot_id}` are invalid. "
                    f"Reason - {exc.message_template}",
                )
                continue

            account.token = token
