"""Implementation for bot classes."""

import asyncio
from typing import (
    Any,
    BinaryIO,
    Callable,
    Dict,
    List,
    Optional,
    Sequence,
    Set,
    TextIO,
    Type,
    Union,
    cast,
)
from uuid import UUID

from loguru import logger

from botx import clients, concurrency, exception_handlers, exceptions, typing, utils
from botx.collecting import Collector, Handler
from botx.dependencies import models as deps
from botx.exceptions import ServerUnknownError
from botx.middlewares.base import BaseMiddleware
from botx.middlewares.exceptions import ExceptionMiddleware
from botx.models import datastructures, enums, files, menu, messages, sending
from botx.models.credentials import ExpressServer, ServerCredentials
from botx.models.requests import (
    AddRemoveUsersPayload,
    StealthDisablePayload,
    StealthEnablePayload,
)


class Bot:  # noqa: WPS214, WPS230
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

    @property
    def handlers(self) -> List[Handler]:
        """Get handlers registered on this bot.

        Returns:
            Registered handlers of bot.
        """
        return self.collector.handlers

    def include_collector(
        self,
        collector: "Collector",
        *,
        dependencies: Optional[Sequence[deps.Depends]] = None,
    ) -> None:
        """Include handlers from collector into bot.

        Arguments:
            collector: collector from which handlers should be copied.
            dependencies: optional sequence of dependencies for handlers for this
                collector.

        Raises:
            AssertionError: raised if both of collectors has registered default handler.
        """
        self.collector.include_collector(collector, dependencies=dependencies)

    def command_for(self, *args: Any) -> str:
        """Find handler and build a command string using passed body params.

        Arguments:
            args: sequence of elements where first element should be name of handler.

        Returns:
            Command string.

        Raises:
            NoMatchFound: raised if handler was no found.
        """
        return self.collector.command_for(*args)

    def handler_for(self, name: str) -> Handler:
        """Find handler in handlers of this bot.

        Find registered handler using using [botx.collector.Collector.handler_for] of
        inner collector.

        Arguments:
            name: name of handler that should be found.

        Returns:
            Handler that was found by name.

        Raises:
            NoMatchFound: raise if handler was not found.
        """
        return self.collector.handler_for(name)

    def add_handler(  # noqa: WPS211
        self,
        handler: Callable,
        *,
        body: Optional[str] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
        full_description: Optional[str] = None,
        include_in_status: Union[bool, Callable] = True,
        dependencies: Optional[Sequence[deps.Depends]] = None,
    ) -> None:
        """Create new handler from passed arguments and store it inside.

        !!! info
            If `include_in_status` is a function, then `body` argument will be checked
            for matching public commands style, like `/command`.

        Arguments:
            handler: callable that will be used for executing handler.
            body: body template that will trigger this handler.
            name: optional name for handler that will be used in generating body.
            description: description for command that will be shown in bot's menu.
            full_description: full description that can be used for example in `/help`
                command.
            include_in_status: should this handler be shown in bot's menu, can be
                callable function with no arguments *(for now)*.
            dependencies: sequence of dependencies that should be executed before
                handler.
        """
        self.collector.add_handler(
            body=body,
            handler=handler,
            name=name,
            description=description,
            full_description=full_description,
            include_in_status=include_in_status,
            dependencies=dependencies,
        )

    def handler(  # noqa: WPS211
        self,
        handler: Optional[Callable] = None,
        *,
        command: Optional[str] = None,
        commands: Optional[Sequence[str]] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
        full_description: Optional[str] = None,
        include_in_status: Union[bool, Callable] = True,
        dependencies: Optional[Sequence[deps.Depends]] = None,
        dependency_overrides_provider: Any = None,
    ) -> Callable:
        """Add new handler to bot.

        !!! info
            If `include_in_status` is a function, then `body` argument will be checked
            for matching public commands style, like `/command`.

        Arguments:
            handler: callable that will be used for executing handler.
            command: body template that will trigger this handler.
            commands: list of body templates that will trigger this handler.
            name: optional name for handler that will be used in generating body.
            description: description for command that will be shown in bot's menu.
            full_description: full description that can be used for example in `/help`
                command.
            include_in_status: should this handler be shown in bot's menu, can be
                callable function with no arguments *(for now)*.
            dependencies: sequence of dependencies that should be executed before
                handler.
            dependency_overrides_provider: mock of callable for handler.

        Returns:
            Passed in `handler` callable.
        """
        return self.collector.handler(
            handler=handler,
            command=command,
            commands=commands,
            name=name,
            description=description,
            full_description=full_description,
            include_in_status=include_in_status,
            dependencies=dependencies,
            dependency_overrides_provider=dependency_overrides_provider,
        )

    def default(  # noqa: WPS211
        self,
        handler: Optional[Callable] = None,
        *,
        command: Optional[str] = None,
        commands: Optional[Sequence[str]] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
        full_description: Optional[str] = None,
        include_in_status: Union[bool, Callable] = False,
        dependencies: Optional[Sequence[deps.Depends]] = None,
        dependency_overrides_provider: Any = None,
    ) -> Callable:
        """Add new handler to bot and register it as default handler.

        !!! info
            If `include_in_status` is a function, then `body` argument will be checked
            for matching public commands style, like `/command`.

        Arguments:
            handler: callable that will be used for executing handler.
            command: body template that will trigger this handler.
            commands: list of body templates that will trigger this handler.
            name: optional name for handler that will be used in generating body.
            description: description for command that will be shown in bot's menu.
            full_description: full description that can be used for example in `/help`
                command.
            include_in_status: should this handler be shown in bot's menu, can be
                callable function with no arguments *(for now)*.
            dependencies: sequence of dependencies that should be executed before
                handler.
            dependency_overrides_provider: mock of callable for handler.

        Returns:
            Passed in `handler` callable.
        """
        return self.collector.default(
            handler=handler,
            command=command,
            commands=commands,
            name=name,
            description=description,
            full_description=full_description,
            include_in_status=include_in_status,
            dependencies=dependencies,
            dependency_overrides_provider=dependency_overrides_provider,
        )

    def hidden(  # noqa: WPS211
        self,
        handler: Optional[Callable] = None,
        *,
        command: Optional[str] = None,
        commands: Optional[Sequence[str]] = None,
        name: Optional[str] = None,
        dependencies: Optional[Sequence[deps.Depends]] = None,
        dependency_overrides_provider: Any = None,
    ) -> Callable:
        """Register hidden handler that won't be showed in menu.

        Arguments:
            handler: callable that will be used for executing handler.
            command: body template that will trigger this handler.
            commands: list of body templates that will trigger this handler.
            name: optional name for handler that will be used in generating body.
            dependencies: sequence of dependencies that should be executed before
                handler.
            dependency_overrides_provider: mock of callable for handler.

        Returns:
            Passed in `handler` callable.
        """
        return self.collector.hidden(
            handler=handler,
            command=command,
            commands=commands,
            name=name,
            dependencies=dependencies,
            dependency_overrides_provider=dependency_overrides_provider,
        )

    def system_event(  # noqa: WPS211
        self,
        handler: Optional[Callable] = None,
        *,
        event: Optional[enums.SystemEvents] = None,
        events: Optional[Sequence[enums.SystemEvents]] = None,
        name: Optional[str] = None,
        dependencies: Optional[Sequence[deps.Depends]] = None,
        dependency_overrides_provider: Any = None,
    ) -> Callable:
        """Register handler for system event.

        Arguments:
            handler: callable that will be used for executing handler.
            event: event for triggering this handler.
            events: a sequence of events that will trigger handler.
            name: optional name for handler that will be used in generating body.
            dependencies: sequence of dependencies that should be executed before
                handler.
            dependency_overrides_provider: mock of callable for handler.

        Returns:
            Passed in `handler` callable.
        """
        return self.collector.system_event(
            handler=handler,
            event=event,
            events=events,
            name=name,
            dependencies=dependencies,
            dependency_overrides_provider=dependency_overrides_provider,
        )

    def chat_created(
        self,
        handler: Optional[Callable] = None,
        *,
        dependencies: Optional[Sequence[deps.Depends]] = None,
        dependency_overrides_provider: Any = None,
    ) -> Callable:
        """Register handler for `system:chat_created` event.

        Arguments:
            handler: callable that will be used for executing handler.
            dependencies: sequence of dependencies that should be executed before
                handler.
            dependency_overrides_provider: mock of callable for handler.

        Returns:
            Passed in `handler` callable.
        """
        return self.collector.chat_created(
            handler=handler,
            dependencies=dependencies,
            dependency_overrides_provider=dependency_overrides_provider,
        )

    def file_transfer(
        self,
        handler: Optional[Callable] = None,
        *,
        dependencies: Optional[Sequence[deps.Depends]] = None,
        dependency_overrides_provider: Any = None,
    ) -> Callable:
        """Register handler for `file_transfer` event.

        Arguments:
            handler: callable that will be used for executing handler.
            dependencies: sequence of dependencies that should be executed before
                handler.
            dependency_overrides_provider: mock of callable for handler.

        Returns:
            Passed in `handler` callable.
        """
        return self.collector.file_transfer(
            handler=handler,
            dependencies=dependencies,
            dependency_overrides_provider=dependency_overrides_provider,
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
            raise ServerUnknownError(f"unknown server {msg.host}")

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

    async def send_message(
        self,
        text: str,
        credentials: sending.SendingCredentials,
        *,
        file: Optional[Union[BinaryIO, TextIO]] = None,
        markup: Optional[sending.MessageMarkup] = None,
        options: Optional[sending.MessageOptions] = None,
    ) -> Optional[UUID]:
        """Send message as answer to command or notification to chat and get it id.

        Arguments:
            text: text that should be sent to client.
            credentials: credentials that are used for sending message.
            file: file that should be attached to message.
            markup: message markup that should be attached to message.
            options: extra options for message.

        Returns:
            `UUID` if message was send as command result or `None` if message was send
            as notification.
        """
        await self._obtain_token(credentials)

        payload = sending.MessagePayload(
            text=text,
            file=files.File.from_file(file) if file else None,
            markup=markup or sending.MessageMarkup(),
            options=options or sending.MessageOptions(),
        )

        if credentials.sync_id:
            return await self.client.send_command_result(credentials, payload)

        return await self.client.send_notification(credentials, payload)

    async def send(self, message: messages.SendingMessage) -> Optional[UUID]:
        """Send message as answer to command or notification to chat and get it id.

        Arguments:
            message: message that should be sent to chat.

        Returns:
            `UUID` of sent event if message was send as command result or `None` if
            message was send as notification.
        """
        await self._obtain_token(message.credentials)

        if message.sync_id:
            return await self.client.send_command_result(
                message.credentials, message.payload
            )

        return await self.client.send_notification(message.credentials, message.payload)

    async def answer_message(
        self,
        text: str,
        message: messages.Message,
        *,
        file: Optional[Union[BinaryIO, TextIO, files.File]] = None,
        markup: Optional[sending.MessageMarkup] = None,
        options: Optional[sending.MessageOptions] = None,
    ) -> UUID:
        """Answer on incoming message and return id of new message..

        !!! warning
            This method should be used only in handlers.

        Arguments:
            text: text that should be sent in message.
            message: incoming message.
            file: file that can be attached to the message.
            markup: bubbles and keyboard that can be attached to the message.
            options: additional message options, like mentions or notifications
                configuration.

        Returns:
            `UUID` of sent event.
        """
        sending_message = messages.SendingMessage(
            text=text, credentials=message.credentials, markup=markup, options=options
        )
        if file:
            sending_message.add_file(file)

        return cast(UUID, await self.send(sending_message))

    async def update_message(
        self, credentials: sending.SendingCredentials, update: sending.UpdatePayload
    ) -> None:
        """Change message by it's event id.

        Arguments:
            credentials: credentials that are used for sending message. *sync_id* is
                required for credentials.
            update: update of message content.
        """
        await self._obtain_token(credentials)
        await self.client.edit_event(credentials, update)

    async def send_file(
        self,
        file: Union[TextIO, BinaryIO, files.File],
        credentials: sending.SendingCredentials,
        filename: Optional[str] = None,
    ) -> Optional[UUID]:
        """Send file in chat and return id of message.

        Arguments:
            file: file-like object that will be sent to chat.
            credentials: credentials of chat where file should be sent.
            filename: name for file that will be used if it can not be accessed from
                `file` argument.

        Returns:
            `UUID` of sent event if message was send as command result or `None` if
            message was send as notification.
        """
        message = messages.SendingMessage(credentials=credentials)
        message.add_file(file, filename)
        return await self.send(message)

    async def stealth_enable(
        self,
        credentials: sending.SendingCredentials,
        chat_id: UUID,
        disable_web: bool,
        burn_in: Optional[int],
        expire_in: Optional[int],
    ) -> None:
        """Enable stealth mode

        Arguments:
            credentials: credentials of chat.
            chat_id: id of chat to enable stealth,
            disable_web: disable web client for chat,
            burn_in: time to burn,
            expire_in: time to expire,
        """
        await self._obtain_token(credentials)
        return await self.client.stealth_enable(
            credentials=credentials,
            payload=StealthEnablePayload(
                group_chat_id=chat_id,
                disable_web=disable_web,
                burn_in=burn_in,
                expire_in=expire_in,
            ),
        )

    async def stealth_disable(
        self, credentials: sending.SendingCredentials, chat_id: UUID,
    ) -> None:
        """Disable stealth mode

        Arguments:
            credentials: credentials of chat.
            chat_id: id of chat to disable stealth,
        """
        await self._obtain_token(credentials)
        return await self.client.stealth_disable(
            credentials=credentials,
            payload=StealthDisablePayload(group_chat_id=chat_id,),
        )

    async def add_users(
        self,
        credentials: sending.SendingCredentials,
        chat_id: UUID,
        users_huids: List[UUID],
    ) -> None:
        """Add users to chat.

        Arguments:
            credentials: credentials of chat.
            chat_id: id of chat to add users,
            users_huids: list of user's huids
        """
        await self._obtain_token(credentials)
        return await self.client.add_users(
            credentials=credentials,
            payload=AddRemoveUsersPayload(
                group_chat_id=chat_id, user_huids=users_huids
            ),
        )

    async def remove_users(
        self,
        credentials: sending.SendingCredentials,
        chat_id: UUID,
        users_huids: List[UUID],
    ) -> None:
        """Remove users from chat.

        Arguments:
            credentials: credentials of chat.
            chat_id: id of chat to remove users,
            users_huids: list of user's huids
        """
        await self._obtain_token(credentials)
        return await self.client.remove_users(
            credentials=credentials,
            payload=AddRemoveUsersPayload(
                group_chat_id=chat_id, user_huids=users_huids
            ),
        )

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

    async def _obtain_token(self, credentials: sending.SendingCredentials) -> None:
        """Get token for bot and fill credentials.

        Arguments:
            credentials: credentials that should be filled with token.
        """
        assert credentials.host, "host is required in credentials for obtaining token"
        assert (
            credentials.bot_id
        ), "bot_id is required in credentials for obtaining token"

        cts = self._get_cts_by_host(credentials.host)

        if cts.server_credentials and cts.server_credentials.token:
            credentials.token = cts.server_credentials.token
            return

        signature = cts.calculate_signature(credentials.bot_id)
        token = await self.client.obtain_token(
            credentials.host, credentials.bot_id, signature
        )
        cts.server_credentials = ServerCredentials(
            bot_id=credentials.bot_id, token=token
        )
        credentials.token = token

    def _get_cts_by_host(self, host: str) -> ExpressServer:
        """Find CTS in bot registered servers.

        Arguments:
            host: host of server that should be found.

        Returns:
            Found instance of registered server.

        Raises:
            ServerUnknownError: raised if server was not found.
        """
        for cts in self.known_hosts:
            if cts.host == host:
                return cts

        raise ServerUnknownError(f"unknown server {host}")
