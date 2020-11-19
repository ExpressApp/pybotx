"""Mixin that defines handler decorator."""

from typing import Any, Callable, Optional, Sequence

from botx.collecting.collectors.collector import Collector
from botx.dependencies.models import Depends
from botx.models.enums import SystemEvents


class SystemEventsHandlerMixin:
    """Mixin that defines handler decorator."""

    collector: Collector

    def system_event(  # noqa: WPS211
        self,
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
        self,
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
        self,
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

    def added_to_chat(
        self,
        handler: Optional[Callable] = None,
        *,
        dependencies: Optional[Sequence[Depends]] = None,
        dependency_overrides_provider: Any = None,
    ) -> Callable:
        """Register handler for `added_to_chat` event.

        Arguments:
            handler: callable that will be used for executing handler.
            dependencies: sequence of dependencies that should be executed before
                handler.
            dependency_overrides_provider: mock of callable for handler.

        Returns:
            Passed in `handler` callable.
        """
        return self.collector.added_to_chat(
            handler=handler,
            dependencies=dependencies,
            dependency_overrides_provider=dependency_overrides_provider,
        )

    def deleted_from_chat(
        self,
        handler: Optional[Callable] = None,
        *,
        dependencies: Optional[Sequence[Depends]] = None,
        dependency_overrides_provider: Any = None,
    ) -> Callable:
        """Register handler for `deleted_from_chat` event.

        Arguments:
            handler: callable that will be used for executing handler.
            dependencies: sequence of dependencies that should be executed before
                handler.
            dependency_overrides_provider: mock of callable for handler.

        Returns:
            Passed in `handler` callable.
        """
        return self.collector.deleted_from_chat(
            handler=handler,
            dependencies=dependencies,
            dependency_overrides_provider=dependency_overrides_provider,
        )

    def left_from_chat(
        self,
        handler: Optional[Callable] = None,
        *,
        dependencies: Optional[Sequence[Depends]] = None,
        dependency_overrides_provider: Any = None,
    ) -> Callable:
        """Register handler for `left_from_chat` event.

        Arguments:
            handler: callable that will be used for executing handler.
            dependencies: sequence of dependencies that should be executed before
                handler.
            dependency_overrides_provider: mock of callable for handler.

        Returns:
            Passed in `handler` callable.
        """
        return self.collector.left_from_chat(
            handler=handler,
            dependencies=dependencies,
            dependency_overrides_provider=dependency_overrides_provider,
        )
