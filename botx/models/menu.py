"""Pydantic models for bot menu."""

from typing import List

from pydantic import BaseModel

from botx.models.enums import Statuses


class MenuCommand(BaseModel):
    """Command that is shown in bot menu."""

    #: command description that will be shown in menu.
    description: str

    #: command body that will trigger command execution.
    body: str

    #: command name.
    name: str


class StatusResult(BaseModel):
    """Bot menu commands collection."""

    #: is bot enabled.
    enabled: bool = True

    #: status of bot.
    status_message: str = "Bot is working"

    #: list of bot commands that will be shown in menu.
    commands: List[MenuCommand] = []


class Status(BaseModel):
    """Object that should be returned on `/status` request from BotX API."""

    #: operation status.
    status: Statuses = Statuses.ok

    #: bot status.
    result: StatusResult = StatusResult()
