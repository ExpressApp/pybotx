"""Definition for command handler."""

from __future__ import annotations

import re
from dataclasses import field
from typing import Any, Callable, List, Optional, Union

from pydantic import validator
from pydantic.dataclasses import dataclass

from botx.collecting.handlers.validators import (
    check_handler_is_function,
    retrieve_dependant,
    retrieve_executor,
    retrieve_full_description_for_handler,
    retrieve_name_for_handler,
    validate_body_for_status,
)
from botx.dependencies import models as deps
from botx.models.messages.message import Message


@dataclass
class Handler:
    """Handler that will store body and callable."""

    #: callable for executing registered logic.
    handler: Callable

    #: command body.
    body: str

    #: name of handler.
    name: str = ""

    #: description that will be shown in bot's menu.
    description: Optional[str] = None

    #: custom description that can be used for another purposes.
    full_description: str = ""

    #: should handler be included into status.
    include_in_status: Union[bool, Callable] = True

    #: wrapper around handler that will be executed.
    dependant: deps.Dependant = field(init=False)

    #: background dependencies for handler.
    dependencies: List[deps.Depends] = field(default_factory=list)

    #: custom object that will override dependencies for handler.
    dependency_overrides_provider: Optional[Any] = None

    #: function that will be used for handling incoming message
    executor: Callable = field(init=False)

    _body_validator = validator("executor", always=True)(validate_body_for_status)
    _handler_is_function_validator = validator("handler", pre=True, always=True)(
        check_handler_is_function,
    )

    async def __call__(self, message: Message) -> None:
        """Execute handler using incoming message.

        Arguments:
            message: message that will be handled by handler.
        """
        await self.executor(message)

    def __post_init__(self) -> None:
        """Initialize or update special fields."""
        self.name = retrieve_name_for_handler(self.name, self.handler)
        self.full_description = retrieve_full_description_for_handler(
            self.full_description, self.handler,
        )
        self.dependant = retrieve_dependant(self.handler, self.dependencies)
        self.executor = retrieve_executor(  # type: ignore
            self.dependant, self.dependency_overrides_provider,
        )

    def matches(self, message: Message) -> bool:
        """Check if message body matched to handler's body.

        Arguments:
            message: incoming message which body will be used to check route.

        Returns:
            Result of check.
        """
        return bool(re.compile(self.body).match(message.body))

    def command_for(self, *args: Any) -> str:
        """Build a command string using passed body query_params.

        Arguments:
            args: sequence of elements that are arguments for command.

        Returns:
            Built command.
        """
        args_str = " ".join((str(arg) for arg in args[1:]))
        return "{0} {1}".format(self.body, args_str).strip()

    def __eq__(self, other: object) -> bool:
        """Compare 2 handlers for equality.

        Arguments:
            other: handler to compare with.

        Returns:
            Result of comparing.
        """
        if not isinstance(other, Handler):
            return False

        callable_comp = self.handler == other.handler
        callable_comp = callable_comp and self.dependencies == other.dependencies

        export_comp = self.name == other.name
        export_comp = export_comp and self.body == other.body
        export_comp = export_comp and self.description == other.description
        export_comp = export_comp and self.full_description == other.full_description
        export_comp = export_comp and self.include_in_status == other.include_in_status

        return callable_comp and export_comp
