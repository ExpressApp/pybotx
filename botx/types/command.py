from typing import Any, Dict

from .base import BotXType


class MessageCommand(BotXType):
    body: str
    data: Dict[str, Any] = {}

    @property
    def cmd(self) -> str:
        return self.body.split(" ", 1)[0]

    @property
    def cmd_arg(self) -> str:
        return "".join(self.body.split(" ", 1)[1:])
