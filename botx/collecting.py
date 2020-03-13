"""Definition of command handlers and routing mechanism."""

import inspect
import re
from functools import partial
from typing import Any, Awaitable, Callable, List, Optional, Sequence, Union

from loguru import logger

from botx import concurrency, utils
from botx.dependencies import models as deps
from botx.dependencies.solving import solve_dependencies
from botx.exceptions import NoMatchFound
from botx.models import enums, messages

SLASH = "/"


def get_body_from_name(name: str) -> str:
    """Get auto body from given handler name in format `/word-word`.

    Examples:
        ```
        >>> get_body_from_name("HandlerFunction")
        "handler-function"
        >>> get_body_from_name("handlerFunction")
        "handler-function"
        ```
    Arguments:
        name: name of handler for which body should be generated.
    """
    splited_words = re.findall(r"^[a-z\d_\-]+|[A-Z\d_\-][^A-Z\d_\-]*", name)
    joined_body = "-".join(splited_words)
    dashed_body = joined_body.replace("_", "-")
    return "/{0}".format(re.sub(r"-+", "-", dashed_body).lower())


def get_executor(
    dependant: deps.Dependant, dependency_overrides_provider: Any = None
) -> Callable[[messages.Message], Awaitable[None]]:
    """Get an execution callable for passed dependency.

    Arguments:
        dependant: passed dependency for which execution callable should be generated.
        dependency_overrides_provider: dependency overrider that will be passed to the
            execution.

    Raises:
        AssertationError: raise if there is no callable in `dependant.call`.
    """
    assert dependant.call is not None, "dependant.call must be a function"

    async def factory(message: messages.Message) -> None:
        values, _ = await solve_dependencies(
            message=message,
            dependant=dependant,
            dependency_overrides_provider=dependency_overrides_provider,
        )
        assert dependant.call is not None, "dependant.call must be a function"
        await concurrency.callable_to_coroutine(dependant.call, **values)

    return factory


class Handler:  # noqa: WPS230
    """Handler that will store body and callable."""

    def __init__(  # noqa: WPS211, WPS213
        self,
        body: str,
        handler: Callable,
        *,
        name: Optional[str] = None,
        description: Optional[str] = None,
        full_description: Optional[str] = None,
        include_in_status: Union[bool, Callable] = True,
        dependencies: Optional[Sequence[deps.Depends]] = None,
        dependency_overrides_provider: Any = None,
    ) -> None:
        """Init handler that will be used for executing registered logic.

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
            dependency_overrides_provider: mock of callable for handler.
        """
        if include_in_status:
            assert body.startswith(
                SLASH
            ), "Public commands should start with leading slash"
            assert (
                body[: -len(body.strip(SLASH))].count(SLASH) == 1
            ), "Command body can contain only single leading slash"
            assert (
                len(body.split()) == 1
            ), "Public commands should contain only one word"

        self.body: str = body
        """Command body."""
        self.handler: Callable = handler
        """Callable for executing registered logic."""
        self.name: str = utils.get_name_from_callable(handler) if name is None else name
        """Name of handler."""

        self.dependencies: List[deps.Depends] = utils.optional_sequence_to_list(
            dependencies
        )
        """Additional dependencies of handler."""
        self.description: Optional[str] = description
        """Description that will be used in bot's menu."""
        self.full_description: str = full_description or inspect.cleandoc(
            handler.__doc__ or ""
        )
        """Extra description."""
        self.include_in_status: Union[bool, Callable] = include_in_status
        """Flag or function that will check if command should be showed in menu."""

        assert inspect.isfunction(handler) or inspect.ismethod(
            handler
        ), f"Handler must be a function or method"
        self.dependant: deps.Dependant = deps.get_dependant(call=self.handler)
        """Dependency for passed handler."""
        for index, depends in enumerate(self.dependencies):
            assert callable(
                depends.dependency
            ), "A parameter-less dependency must have a callable dependency"
            self.dependant.dependencies.insert(
                index,
                deps.get_dependant(
                    call=depends.dependency, use_cache=depends.use_cache
                ),
            )
        self.dependency_overrides_provider: Any = dependency_overrides_provider
        """Overrider for passed dependencies."""
        self.executor: Callable = get_executor(
            dependant=self.dependant,
            dependency_overrides_provider=self.dependency_overrides_provider,
        )
        """Main logic executor for passed handler."""

    def matches(self, message: messages.Message) -> bool:
        """Check if message body matched to handler's body.

        Arguments:
            message: incoming message which body will be used to check route.
        """
        return bool(re.compile(self.body).match(message.body))

    def command_for(self, *args: Any) -> str:
        """Build a command string using passed body params.

        Arguments:
            args: sequence of elements that are arguments for command.
        """
        args_str = " ".join((str(arg) for arg in args[1:]))
        return "{0} {1}".format(self.body, args_str).strip()

    async def __call__(self, message: messages.Message) -> None:
        """Execute handler using incoming message.

        Arguments:
            message: message that will be handled by handler.
        """
        await self.executor(message)


class Collector:  # noqa: WPS214, WPS230
    """Collector for different handlers."""

    def __init__(
        self,
        handlers: Optional[List[Handler]] = None,
        default: Optional[Handler] = None,
        dependencies: Optional[Sequence[deps.Depends]] = None,
        dependency_overrides_provider: Any = None,
    ) -> None:
        """Init collector with required params.

        Arguments:
            handlers: list of handlers that will be stored in this collector after init.
            default: default handler that will be used if no handler found.
            dependencies: background dependencies for all handlers applied to this
                collector.
            dependency_overrides_provider: object that will override dependencies for
                this handler.
        """
        self.handlers: List[Handler] = []
        """List of registered on this collector handlers in order of adding."""
        self._added_handlers: List[Handler] = []
        self.dependencies: Optional[Sequence[deps.Depends]] = dependencies
        """Background dependencies that will be executed for handlers."""
        self.dependency_overrides_provider: Any = dependency_overrides_provider
        """Overrider for dependencies."""
        self.default_message_handler: Optional[Handler] = None
        """Handler that will be used for handling non matched message."""

        handlers = utils.optional_sequence_to_list(handlers)

        self._add_handlers(handlers)

        if default:
            default_dependencies = list(dependencies or []) + list(
                default.dependencies or []
            )
            self.default_message_handler = Handler(
                body=default.body,
                handler=default.handler,
                name=default.name,
                description=default.description,
                full_description=default.full_description,
                include_in_status=default.include_in_status,
                dependencies=default_dependencies,
                dependency_overrides_provider=self.dependency_overrides_provider,
            )

    def include_collector(
        self,
        collector: "Collector",
        *,
        dependencies: Optional[Sequence[deps.Depends]] = None,
    ) -> None:
        """Include handlers from another collector into this one.

        Arguments:
            collector: collector from which handlers should be copied.
            dependencies: optional sequence of dependencies for handlers for this
                collector.
        """
        assert not (
            self.default_message_handler and collector.default_message_handler
        ), "Only one default handler can be applied"

        if collector.default_message_handler:
            self.default_message_handler = collector.default_message_handler

        self._add_handlers(collector.handlers, dependencies)

    def command_for(self, *args: Any) -> str:
        """Find handler and build a command string using passed body params.

        Arguments:
            args: sequence of elements where first element should be name of handler.

        Returns:
            Command string.

        Raises:
            NoMatchFound: raised if handler was no found.
        """
        if not len(args):
            raise TypeError("missing handler name as the first argument")

        for handler in self.handlers:
            if handler.name == args[0]:
                return handler.command_for(*args)

        raise NoMatchFound

    def handler_for(self, name: str) -> Handler:
        """Find handler in handlers of this bot.

        Arguments:
            name: name of handler that should be found.

        Returns:
            Handler that was found by name.

        Raises:
            NoMatchFound: raise if handler was not found.
        """

        for handler in self.handlers:
            if handler.name == name:
                return handler

        raise NoMatchFound

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
        dependency_overrides_provider: Any = None,
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
            dependency_overrides_provider: mock of callable for handler.
        """
        if body is None:
            name = name or utils.get_name_from_callable(handler)
            body = get_body_from_name(name)

        for registered_handler in self.handlers:
            assert (
                body.strip(SLASH) != ""
            ), "Handler should not consist only from slashes"
            assert (
                body != registered_handler.body
            ), f"Handler with body {registered_handler.body} already registered"
            assert (
                name != registered_handler.name
            ), f"Handler with name {registered_handler.name} already registered"

        dep_override = (
            dependency_overrides_provider or self.dependency_overrides_provider
        )
        updated_dependencies = utils.optional_sequence_to_list(
            self.dependencies
        ) + utils.optional_sequence_to_list(dependencies)
        command_handler = Handler(
            body=body,
            handler=handler,
            name=name,
            description=description,
            full_description=full_description,
            include_in_status=include_in_status,
            dependencies=updated_dependencies,
            dependency_overrides_provider=dep_override,
        )
        self.handlers.append(command_handler)
        self._added_handlers.append(command_handler)
        self._added_handlers.sort(key=lambda handler: len(handler.body), reverse=True)

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
        """Add new handler to collector.

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
        if handler:
            handler_commands: List[Optional[str]] = utils.optional_sequence_to_list(
                commands
            )

            if command and commands:
                handler_commands.insert(0, command)
            elif not commands:
                handler_commands = [command]

            for command_body in handler_commands:
                self.add_handler(
                    body=command_body,
                    handler=handler,
                    name=name,
                    description=description,
                    full_description=full_description,
                    include_in_status=include_in_status,
                    dependencies=dependencies,
                    dependency_overrides_provider=dependency_overrides_provider,
                )

            return handler

        return partial(
            self.handler,
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
        assert (
            not self.default_message_handler
        ), "Default handler is already registered on this collector"

        if handler:
            registered_handler = self.handler(
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
            name = name or utils.get_name_from_callable(registered_handler)
            self.default_message_handler = self.handler_for(name)

            return handler

        return partial(
            self.default,
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
        return self.handler(
            handler=handler,
            command=command,
            commands=commands,
            name=name,
            include_in_status=False,
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
        assert event or events, "At least one event should be passed"

        return self.handler(
            handler=handler,
            command=event.value if event else None,
            commands=[event.value for event in events] if events else None,
            name=name,
            include_in_status=False,
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
        return self.system_event(
            handler=handler,
            event=enums.SystemEvents.chat_created,
            name=enums.SystemEvents.chat_created.value,
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
        return self.system_event(
            handler=handler,
            event=enums.SystemEvents.file_transfer,
            name=enums.SystemEvents.file_transfer.value,
            dependencies=dependencies,
            dependency_overrides_provider=dependency_overrides_provider,
        )

    async def handle_message(self, message: messages.Message) -> None:
        """Find handler and execute it.

        Arguments:
            message: incoming message that will be passed to handler.
        """
        for handler in self.handlers:
            if handler.matches(message):
                logger.bind(botx_collector=True).info(
                    f"botx => {handler.name}: {message.command.command}"
                )
                await handler(message)
                return

        if self.default_message_handler:
            await self.default_message_handler(message)
        else:
            raise NoMatchFound

    async def __call__(self, message: messages.Message) -> None:
        """Find handler and execute it.

        Arguments:
            message: incoming message that will be passed to handler.
        """
        await self.handle_message(message)

    def _add_handlers(
        self,
        handlers: List[Handler],
        dependencies: Optional[Sequence[deps.Depends]] = None,
    ) -> None:
        """Add list of handlers with dependencies to collector.

        Arguments:
            handlers: list of handlers that should be added to this collector.
            dependencies: additional dependencies that will be applied for all handlers.
        """
        for handler in handlers:
            self.add_handler(
                body=handler.body,
                handler=handler.handler,
                name=handler.name,
                description=handler.description,
                full_description=handler.full_description,
                include_in_status=handler.include_in_status,
                dependencies=handler.dependencies,
            )
            created_handler = self.handler_for(handler.name)
            created_handler.dependencies = utils.optional_sequence_to_list(
                dependencies
            ) + utils.optional_sequence_to_list(created_handler.dependencies)
