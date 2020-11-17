"""Definition for mixin with system events decorator."""
from typing import Any, Callable, Optional, Sequence, cast

from botx.collecting.collectors.mixins.handler import HandlerDecoratorProtocol
from botx.dependencies.models import Depends
from botx.models.enums import SystemEvents

try:
    from typing import Protocol  # noqa: WPS433
except ImportError:
    from typing_extensions import Protocol  # type: ignore  # noqa: WPS433, WPS440, F401


class SystemEventsHandlerMixin:
    """Mixin that defines system events handler decorator."""

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

        Raises:
            AssertionError: raised if nor event or events passed.
        """
        if not (event or events):
            raise AssertionError("at least one event should be passed")

        return cast(HandlerDecoratorProtocol, self).handler(
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
        return self.system_event(
            handler=handler,
            event=SystemEvents.chat_created,
            name=SystemEvents.chat_created.value,
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
        return self.system_event(
            handler=handler,
            event=SystemEvents.file_transfer,
            name=SystemEvents.file_transfer.value,
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
        return self.system_event(
            handler=handler,
            event=SystemEvents.added_to_chat,
            name=SystemEvents.added_to_chat.value,
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
        return self.system_event(
            handler=handler,
            event=SystemEvents.deleted_from_chat,
            name=SystemEvents.deleted_from_chat.value,
            dependencies=dependencies,
            dependency_overrides_provider=dependency_overrides_provider,
        )
