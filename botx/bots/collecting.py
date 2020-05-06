"""Definition for bot's collecting component.

All of this methods are just wrappers around inner collector.
"""

from typing import Any, Callable, List, Optional, Sequence, Union

from botx.collecting import Collector, Handler
from botx.dependencies import models as deps
from botx.models import enums


class BotCollectingMixin:
    """Mixin that defines collector-like behaviour."""

    collector: Collector

    @property
    def handlers(self) -> List[Handler]:
        """Get handlers registered on this bot.

        Returns:
            Registered handlers of bot.
        """
        return self.collector.handlers

    def include_collector(
        self,
        collector: Collector,
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
