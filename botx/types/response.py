from enum import Enum
from typing import List, Union
from uuid import UUID

from .base import BotXType
from .bubble import BubbleElement
from .core import MenuCommand, StatusEnum
from .keyboard import KeyboardElement


class ResponseRecipientsEnum(str, Enum):
    all: str = "all"


class ResponseResult(BotXType):
    status: StatusEnum = StatusEnum.ok
    body: str
    commands: List[MenuCommand] = []
    keyboard: List[List[KeyboardElement]] = []
    bubble: List[List[BubbleElement]] = []


class ResponseCommandResult(ResponseResult):
    pass


class ResponseNotificationResult(ResponseResult):
    pass


class ResponseCommand(BotXType):
    sync_id: UUID
    bot_id: UUID
    recipients: Union[List[UUID], ResponseRecipientsEnum] = ResponseRecipientsEnum.all
    command_result: ResponseCommandResult


class ResponseNotification(BotXType):
    bot_id: UUID
    recipients: Union[List[UUID], ResponseRecipientsEnum] = ResponseRecipientsEnum.all
    group_chat_ids: List[UUID] = []
    notification: ResponseNotificationResult


class ResponseDocument(BotXType):
    bot_id: UUID
    sync_id: UUID
