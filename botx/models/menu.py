"""Pydantic models for bot menu."""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel

from botx.models.enums import Statuses


class CommandUIElement(BaseModel):
    """UI elements for commands in menu. *Not used for now*."""

    type: str
    """element type."""
    label: str
    """element title."""
    order: Optional[int] = None
    """order of element on client."""
    value: Optional[Any] = None
    """value of element."""
    name: Optional[str] = None
    """name of element as key, that will be stored in command."""
    disabled: Optional[bool] = None
    """possibility to change element value."""


class MenuCommand(BaseModel):
    """Command that is shown in bot menu."""

    description: str
    """command description that will be shown in menu."""
    body: str
    """command body that will trigger command execution."""
    name: str
    """command name."""
    options: Dict[str, Any] = {}
    """dictionary with command options. *Not used for now*."""
    elements: List[CommandUIElement] = []
    """list of UI elements for command. *Not used for now*."""


class StatusResult(BaseModel):
    """Bot menu commands collection."""

    enabled: bool = True
    """is bot enabled."""
    status_message: str = "Bot is working"
    """status of bot."""
    commands: List[MenuCommand] = []
    """list of bot commands that will be shown in menu."""


class Status(BaseModel):
    """Object that should be returned on `/status` request from BotX API."""

    status: Statuses = Statuses.ok
    """operation status."""
    result: StatusResult = StatusResult()
    """bot status."""
