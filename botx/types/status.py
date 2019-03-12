from typing import List, Optional

from .base import BotXType

from .core import MenuCommand, StatusEnum


class StatusResult(BotXType):
    enabled: bool = True
    status_message: Optional[str] = None
    commands: List[MenuCommand] = []


class Status(BotXType):
    status: StatusEnum = StatusEnum.ok
    result: StatusResult = StatusResult()
