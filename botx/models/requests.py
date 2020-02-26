"""Pydantic models for requests to BotX API."""

from typing import List, Optional, Union
from uuid import UUID

from pydantic import BaseModel, Field

from botx.models.constants import MAXIMUM_TEXT_LENGTH
from botx.models.enums import Recipients, Statuses
from botx.models.files import File
from botx.models.mentions import Mention
from botx.models.menu import MenuCommand
from botx.models.sending import NotificationOptions
from botx.models.typing import BubbleMarkup, KeyboardMarkup


class ResultPayload(BaseModel):
    """Data that is sent when bot answers on command or send notification."""

    status: Statuses = Statuses.ok
    """status of operation. *Not used for now*."""
    body: str = Field("", max_length=MAXIMUM_TEXT_LENGTH)
    """body for new message from bot."""
    commands: List[MenuCommand] = []
    """list of bot commands. *Not used for now*."""
    keyboard: KeyboardMarkup = []
    """keyboard that will be used for new message."""
    bubble: BubbleMarkup = []
    """bubble elements that will be showed under new message."""
    mentions: List[Mention] = []
    """mentions that BotX API will append before new message text."""


class UpdatePayload(BaseModel):
    """Data that is sent when bot updates message."""

    status: Statuses = Statuses.ok
    """status of operation. *Not used for now*."""
    body: Optional[str] = Field(None, max_length=MAXIMUM_TEXT_LENGTH)
    """new body in message."""
    commands: Optional[List[MenuCommand]] = None
    """new list of bot commands. *Not used for now*."""
    keyboard: Optional[KeyboardMarkup] = None
    """new keyboard that will be used for new message."""
    bubble: Optional[BubbleMarkup] = None
    """new bubble elements that will be showed under new message."""
    mentions: Optional[List[Mention]] = None
    """new mentions that BotX API will append before new message text."""


class ResultOptions(BaseModel):
    """Configuration for command result or notification that is send to BotX API."""

    stealth_mode: bool = False
    """send message only when stealth mode is enabled"""
    notification_opts: NotificationOptions = NotificationOptions()
    """message options for configuring notifications."""


class BaseResult(BaseModel):
    """Shared attributes for command result and notification."""

    bot_id: UUID
    """`UUID` of bot that handled operation."""
    recipients: Union[List[UUID], Recipients] = Recipients.all
    """users that will receive recipients or `all` users in chat."""
    file: Optional[File] = None
    """file that will be attached to new message."""
    opts: ResultOptions = ResultOptions()
    """options that control message behaviour."""


class CommandResult(BaseResult):
    """Entity that will be sent to BotX API on command result."""

    sync_id: UUID
    """event id for message that is handled by command."""
    result: ResultPayload = Field(..., alias="command_result")
    """result of operation."""


class Notification(BaseResult):
    """Entity that will be sent to BotX API on notification."""

    group_chat_ids: List[UUID]
    """chat ids that will receive message."""
    result: ResultPayload = Field(..., alias="notification")
    """result of operation."""


class EventEdition(BaseModel):
    """Entity that will be sent to BotX API on event edition."""

    sync_id: UUID
    """id of event that should be edited."""
    result: Union[UpdatePayload] = Field(UpdatePayload(), alias="payload")
    """update for message content."""
    opts: Optional[ResultOptions] = None
    """update for options update. *Not used for now*."""


class StealthDisablePayload(BaseModel):
    """Data structure that will be sent to BotX API to disable stealth mode"""

    group_chat_id: UUID
    """ID of chat"""


class StealthEnablePayload(BaseModel):
    """Data structure that will be sent to BotX API to enable stealth mode"""

    group_chat_id: UUID
    """ID of chat"""
    disable_web: bool = False
    """disable web client for chat"""
    burn_in: Optional[int] = None
    """expire time for read messages, sec"""
    expire_in: Optional[int] = None
    """expire time for unread messages, sec"""


class AddRemoveUsersPayload(BaseModel):
    """Data structure that will be sent to BotX API to add/remove users to/from chat"""

    group_chat_id: UUID
    """ID of chat."""
    user_huids: List[UUID]
    """List of users' huids."""
