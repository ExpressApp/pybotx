"""Definition for base collector."""

from dataclasses import InitVar, field
from typing import Any, Callable, List, Optional, Sequence, Union

from pydantic.dataclasses import dataclass

from botx import converters
from botx.collecting.handlers.handler import Handler
from botx.collecting.handlers.name_generators import (
    get_body_from_name,
    get_name_from_callable,
)
from botx.dependencies import models as deps
from botx.dependencies.models import Depends
from botx.exceptions import NoMatchFound


def _get_sorted_handlers(handlers: List[Handler]) -> List[Handler]:
    return sorted(handlers, key=lambda handler: len(handler.body), reverse=True)


def _combine_dependencies(
    *dependencies: Optional[Sequence[deps.Depends]],
) -> List[deps.Depends]:
    result_dependencies = []
    for deps_sequence in dependencies:
        result_dependencies.extend(converters.optional_sequence_to_list(deps_sequence))

    return result_dependencies


def _check_new_handler_restrictions(
    body: str, name: Optional[str], handler: Callable, existed_handler: Handler,
) -> None:
    handler_executor = existed_handler.handler
    handler_name = existed_handler.name

    if body == existed_handler.body:
        raise AssertionError("handler with body {0} already registered".format(body))

    handler_registered = handler == handler_executor and name == handler_name
    if name == existed_handler.name and not handler_registered:
        raise AssertionError("handler with name {0} already registered".format(name))


@dataclass
class BaseCollector:
    """Base collector."""

    default: InitVar[Handler] = None

    #: registered handlers on this collector handlers in order of adding.
    handlers: List[Handler] = field(default_factory=list)

    #: handler that will be used for handling non matched message.
    default_message_handler: Optional[Handler] = None

    #: background dependencies that will be executed for handlers.
    dependencies: Optional[Sequence[Depends]] = None

    #: overrider for dependencies.
    dependency_overrides_provider: Optional[Any] = None

    @property
    def sorted_handlers(self) -> List[Handler]:
        """Get added handlers sorted by bodies length.

        Returns:
            Sorted handlers.
        """
        return _get_sorted_handlers(self.handlers)

    def __post_init__(self, default: Optional[Handler]) -> None:
        """Initialize or update special fields.

        Arguments:
            default: callable that should be used as default handler.
        """
        handlers = self.handlers
        self.handlers = []
        self._add_handlers(converters.optional_sequence_to_list(handlers))

        if default is not None:
            self._add_default_handler(default)

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

        raise NoMatchFound(search_param=name)

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
            name = name or get_name_from_callable(handler)
            body = get_body_from_name(name)

        for registered_handler in self.handlers:
            _check_new_handler_restrictions(body, name, handler, registered_handler)

        dep_override = (
            dependency_overrides_provider
            if dependency_overrides_provider is not None
            else self.dependency_overrides_provider
        )
        command_handler = Handler(
            body=body,
            handler=handler,
            name=name,  # type: ignore
            description=description,
            full_description=full_description,  # type: ignore
            include_in_status=include_in_status,
            dependencies=_combine_dependencies(self.dependencies, dependencies),
            dependency_overrides_provider=dep_override,
        )
        self.handlers.append(command_handler)

    def _add_handlers(
        self, handlers: List[Handler], dependencies: Optional[Sequence[Depends]] = None,
    ) -> None:
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
            created_handler.dependencies = _combine_dependencies(
                dependencies, created_handler.dependencies,
            )

    def _add_default_handler(
        self, default: Handler, dependencies: Optional[Sequence[Depends]] = None,
    ) -> None:
        default_dependencies = _combine_dependencies(
            self.dependencies, dependencies, default.dependencies,
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
