from typing import Any, Callable, Dict, List, Optional, Tuple

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
    command: str
    description: str
    callback: CommandCallback
    full_description: Optional[str] = ""
    command_params: List[str] = []
    exclude_from_status: bool = False
    use_as_default_handler: bool = False
    options: Dict[str, Any] = {}
    elements: List[CommandUIElement] = []

    def to_status_command(self) -> Optional[MenuCommand]:
        if not self.exclude_from_status and not self.use_as_default_handler:
            return MenuCommand(
                body=self.command,
                name=self.name,
                description=self.description,
                options=self.options,
                elements=self.elements,
            )

        return None
