from typing import List

from .base import BotXType
from .core import MenuCommand, StatusEnum


class StatusResult(BotXType):
    enabled: bool = True
    status_message: str = "Bot is working"
    commands: List[MenuCommand] = []


class Status(BotXType):
    status: StatusEnum = StatusEnum.ok
    result: StatusResult = StatusResult()
