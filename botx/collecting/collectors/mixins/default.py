"""Definition for mixin with default decorator."""
from functools import partial
from typing import Any, Callable, Optional, Sequence, Union, cast

from botx.collecting.collectors.mixins.handler import HandlerDecoratorProtocol
from botx.collecting.handlers.handler import Handler
from botx.collecting.handlers.name_generators import get_name_from_callable
from botx.dependencies.models import Depends

try:
    from typing import Protocol  # noqa: WPS433
except ImportError:
    from typing_extensions import Protocol  # type: ignore  # noqa: WPS433, WPS440, F401


class HandlerSearchProtocol(Protocol):
    """Protocol for searching handler."""

    def handler_for(self, name: str) -> Handler:
        """Find handler in handlers of this bot."""


class DefaultHandlerMixin:
    """Mixin that defines default handler decorator."""

    default_message_handler: Optional[Handler]

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
        dependencies: Optional[Sequence[Depends]] = None,
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

        Raises:
            AssertionError: raised if default handler already defined on collector.
        """
        if self.default_message_handler is not None:
            raise AssertionError(
                "default handler is already registered on this collector",
            )

        if handler:
            registered_handler = cast(HandlerDecoratorProtocol, self).handler(
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
            name = name or get_name_from_callable(registered_handler)
            self.default_message_handler = cast(
                HandlerSearchProtocol,
                self,
            ).handler_for(name)

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
