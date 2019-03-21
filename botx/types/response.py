from typing import List, Optional, Union
from uuid import UUID

from .base import BotXType
from .bubble import BubbleElement
from .core import MenuCommand, ResponseRecipientsEnum, StatusEnum, SyncID
from .file import File
from .keyboard import KeyboardElement
from .mention import Mention


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
    sync_id: SyncID
    bot_id: UUID
    recipients: Union[List[UUID], ResponseRecipientsEnum] = ResponseRecipientsEnum.all
    command_result: ResponseCommandResult
    mentions: List[Mention] = []
    file: Optional[File] = None


class ResponseNotification(BotXType):
    bot_id: UUID
    recipients: Union[List[UUID], ResponseRecipientsEnum] = ResponseRecipientsEnum.all
    group_chat_ids: List[UUID] = []
    notification: ResponseNotificationResult
    mentions: List[Mention] = []
    file: Optional[File] = None


class ResponseFile(BotXType):
    bot_id: UUID
    sync_id: SyncID
