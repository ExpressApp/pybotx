import re
from typing import Any, Callable, Dict, List, Optional, Pattern, Tuple

from .base import BotXType
from .common import CommandUIElement
from .status import MenuCommand


class Dependency(BotXType):
    call: Callable


class CommandCallback(BotXType):
    callback: Callable
    args: Tuple[Any, ...] = ()
    kwargs: Dict[str, Any] = {}
    background_dependencies: List[Dependency] = []


class CommandHandler(BotXType):
    name: str
    command: Pattern
    description: str
    callback: CommandCallback
    exclude_from_status: bool = False
    use_as_default_handler: bool = False
    options: Dict[str, Any] = {}
    elements: List[CommandUIElement] = []

    def to_status_command(self) -> Optional[MenuCommand]:
        if not self.exclude_from_status and not self.use_as_default_handler:
            unescaped_command_body = re.sub(r"\\(.)", r"\1", self.command.pattern)
            return MenuCommand(
                body=unescaped_command_body,
                name=self.name,
                description=self.description,
                options=self.options,
                elements=self.elements,
            )

        return None
