"""Mixin that defines handler decorator."""

from typing import Any, Callable, Optional, Sequence

from botx.collecting.collectors.collector import Collector
from botx.dependencies.models import Depends
from botx.models.command import CommandDescriptor


class HiddenHandlerMixin:
    """Mixin that defines handler decorator."""

    collector: Collector

    def hidden(  # noqa: WPS211
        self,
        handler: Optional[Callable] = None,
        *,
        command: Optional[str] = None,
        commands: Optional[Sequence[str]] = None,
        name: Optional[str] = None,
        command_descriptor: Optional[CommandDescriptor] = None,
        dependencies: Optional[Sequence[Depends]] = None,
        dependency_overrides_provider: Any = None,
    ) -> Callable:
        """Register hidden handler that won't be showed in menu.

        Arguments:
            handler: callable that will be used for executing handler.
            command: body template that will trigger this handler.
            commands: list of body templates that will trigger this handler.
            name: optional name for handler that will be used in generating body.
            command_descriptor: parameter object including `command`, `commands`,
                `name` and `description`. Separately passed any of these has priority
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
            command_descriptor=command_descriptor,
            dependencies=dependencies,
            dependency_overrides_provider=dependency_overrides_provider,
        )
