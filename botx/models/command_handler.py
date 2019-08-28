from typing import Any, Callable, Dict, List, Optional, Pattern, Tuple, Type, Union

from pydantic import validator

from botx.core import PRIMITIVE_TYPES

from .base import BotXType
from .common import CommandUIElement
from .status import MenuCommand

PRIMITIVE_TYPES_ALIAS = Union[Type[int], Type[float], Type[bool], Type[str]]


class Dependency(BotXType):
    call: Callable


class CommandCallback(BotXType):
    callback: Callable
    args: Tuple[Any, ...] = ()
    kwargs: Dict[str, Any] = {}
    background_dependencies: List[Dependency] = []
    command_params: Dict[str, type] = {}

    @validator("command_params")
    def check_params_for_acceptable_types(
        cls, param_type: PRIMITIVE_TYPES_ALIAS
    ) -> PRIMITIVE_TYPES_ALIAS:
        if param_type not in PRIMITIVE_TYPES:
            raise ValueError(
                f"command_params can be {PRIMITIVE_TYPES}, not {param_type}"
            )

        return param_type


class CommandHandler(BotXType):
    name: str
    command: str
    menu_command: str
    regex_command: Pattern
    description: str
    callback: CommandCallback

    full_description: str = ""
    command_params: List[str] = []
    exclude_from_status: bool = False
    use_as_default_handler: bool = False
    options: Dict[str, Any] = {}
    elements: List[CommandUIElement] = []

    def to_status_command(self) -> Optional[MenuCommand]:
        if not (self.exclude_from_status or self.use_as_default_handler):
            return MenuCommand(
                body=self.menu_command,
                name=self.name,
                description=self.description,
                options=self.options,
                elements=self.elements,
            )

        return None
