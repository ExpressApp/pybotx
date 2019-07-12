from typing import List, Optional, Union
from uuid import UUID

from pydantic import Schema

from botx.core import TEXT_MAX_LENGTH

from .base import BotXType
from .common import MenuCommand, NotificationOpts, SyncID
from .enums import ResponseRecipientsEnum, StatusEnum
from .file import File
from .mention import Mention
from .ui import BubbleElement, KeyboardElement


class BotXTokenResponse(BotXType):
    result: str


class BotXTokenRequestParams(BotXType):
    signature: str


class BotXResultPayload(BotXType):
    status: StatusEnum = StatusEnum.ok
    body: str
    commands: List[MenuCommand] = []
    keyboard: List[List[KeyboardElement]] = []
    bubble: List[List[BubbleElement]] = []
    mentions: List[Mention] = []


class BotXBasePayload(BotXType):
    bot_id: UUID
    recipients: Union[List[UUID], ResponseRecipientsEnum] = ResponseRecipientsEnum.all
    file: Optional[File] = None
    opts: NotificationOpts = NotificationOpts()


class BotXCommandResultPayload(BotXBasePayload):
    sync_id: SyncID
    command_result: BotXResultPayload


class BotXNotificationPayload(BotXBasePayload):
    group_chat_ids: List[UUID] = []
    notification: BotXResultPayload


class BotXFilePayload(BotXType):
    bot_id: UUID
    sync_id: SyncID


class SendingCredentials(BotXType):
    sync_id: Optional[SyncID] = None
    chat_ids: List[UUID] = []
    bot_id: UUID
    host: str
    token: Optional[str] = None


class MessageMarkup(BotXType):
    bubbles: List[List[BubbleElement]] = []
    keyboard: List[List[KeyboardElement]] = []


class NotifyOptions(BotXType):
    recipients: Union[
        List[UUID], str, ResponseRecipientsEnum
    ] = ResponseRecipientsEnum.all
    mentions: List[Mention] = []
    notifications: NotificationOpts = NotificationOpts()


class SendingPayload(BotXType):
    text: Optional[str] = Schema(None, max_length=TEXT_MAX_LENGTH)
    file: Optional[File] = None
    markup: MessageMarkup = MessageMarkup()
    options: NotifyOptions = NotifyOptions()


class ErrorResponseData(BotXType):
    status_code: int
    body: str


class BotXAPIErrorData(BotXType):
    address: SendingCredentials
    response: ErrorResponseData
