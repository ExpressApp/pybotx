from typing import List, Optional, Union
from uuid import UUID

from .base import BotXType
from .common import MenuCommand, NotificationOpts, SyncID
from .enums import ResponseRecipientsEnum, StatusEnum
from .file import File
from .mention import Mention
from .ui import BubbleElement, KeyboardElement


class ResponseResult(BotXType):
    status: StatusEnum = StatusEnum.ok
    body: str
    commands: List[MenuCommand] = []
    keyboard: List[List[KeyboardElement]] = []
    bubble: List[List[BubbleElement]] = []
    mentions: List[Mention] = []


class BaseResponse(BotXType):
    bot_id: UUID
    recipients: Union[List[UUID], ResponseRecipientsEnum] = ResponseRecipientsEnum.all
    file: Optional[File] = None
    opts: NotificationOpts = NotificationOpts()


class ResponseCommand(BaseResponse):
    sync_id: SyncID
    command_result: ResponseResult


class ResponseNotification(BaseResponse):
    group_chat_ids: List[UUID] = []
    notification: ResponseResult


class ResponseFile(BotXType):
    bot_id: UUID
    sync_id: SyncID
