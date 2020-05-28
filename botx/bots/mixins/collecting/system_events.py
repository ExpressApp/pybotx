"""Mixin that defines handler decorator."""

from typing import Any, Callable, Optional, Sequence

from botx.bots.mixins.collecting.collector_owner import CollectorOwnerProtocol
from botx.dependencies.models import Depends
from botx.models.enums import SystemEvents


class SystemEventsHandlerMixin:
    """Mixin that defines handler decorator."""

    def hidden(  # noqa: WPS211
        self: CollectorOwnerProtocol,
        handler: Optional[Callable] = None,
        *,
        command: Optional[str] = None,
        commands: Optional[Sequence[str]] = None,
        name: Optional[str] = None,
        dependencies: Optional[Sequence[Depends]] = None,
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
        self: CollectorOwnerProtocol,
        handler: Optional[Callable] = None,
        *,
        event: Optional[SystemEvents] = None,
        events: Optional[Sequence[SystemEvents]] = None,
        name: Optional[str] = None,
        dependencies: Optional[Sequence[Depends]] = None,
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
        self: CollectorOwnerProtocol,
        handler: Optional[Callable] = None,
        *,
        dependencies: Optional[Sequence[Depends]] = None,
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
        self: CollectorOwnerProtocol,
        handler: Optional[Callable] = None,
        *,
        dependencies: Optional[Sequence[Depends]] = None,
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
