"""Definition for mixin with hidden decorator."""
from typing import Any, Callable, Optional, Sequence

from botx.collecting.collectors.mixins.handler import HandlerDecoratorProtocol
from botx.dependencies.models import Depends


class HiddenHandlerMixin:
    """Mixin that defines hidden handler decorator."""

    def hidden(  # noqa: WPS211
        self: HandlerDecoratorProtocol,
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
        return self.handler(
            handler=handler,
            command=command,
            commands=commands,
            name=name,
            include_in_status=False,
            dependencies=dependencies,
            dependency_overrides_provider=dependency_overrides_provider,
        )
