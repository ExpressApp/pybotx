from typing import List, Optional, Union
from uuid import UUID

from pydantic import Schema

from botx.core import TEXT_MAX_LENGTH

from .base import BotXType
from .common import MenuCommand, NotificationOpts
from .enums import ResponseRecipientsEnum, StatusEnum
from .file import File
from .mention import Mention
from .ui import BubbleElement, KeyboardElement, add_ui_element


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


class BotXPayloadOptions(BotXType):
    notification_opts: NotificationOpts = NotificationOpts()


class BotXBasePayload(BotXType):
    bot_id: UUID
    recipients: Union[List[UUID], ResponseRecipientsEnum] = ResponseRecipientsEnum.all
    file: Optional[File] = None
    opts: BotXPayloadOptions = BotXPayloadOptions()


class BotXCommandResultPayload(BotXBasePayload):
    sync_id: UUID
    command_result: BotXResultPayload


class BotXNotificationPayload(BotXBasePayload):
    group_chat_ids: List[UUID] = []
    notification: BotXResultPayload


class BotXFilePayload(BotXType):
    bot_id: UUID
    sync_id: UUID


class SendingCredentials(BotXType):
    sync_id: Optional[UUID] = None
    chat_ids: List[UUID] = []
    bot_id: UUID
    host: str
    token: Optional[str] = None


class MessageMarkup(BotXType):
    bubbles: List[List[BubbleElement]] = []
    keyboard: List[List[KeyboardElement]] = []

    def add_bubble(
        self, command: str, label: Optional[str] = None, *, new_row: bool = True
    ) -> None:
        add_ui_element(
            ui_cls=BubbleElement,
            ui_array=self.bubbles,
            command=command,
            label=label,
            new_row=new_row,
        )

    def add_keyboard_button(
        self, command: str, label: Optional[str] = None, *, new_row: bool = True
    ) -> None:
        add_ui_element(
            ui_cls=KeyboardElement,
            ui_array=self.keyboard,
            command=command,
            label=label,
            new_row=new_row,
        )


class MessageOptions(BotXType):
    recipients: Union[
        List[UUID], str, ResponseRecipientsEnum
    ] = ResponseRecipientsEnum.all
    mentions: List[Mention] = []
    notifications: NotificationOpts = NotificationOpts()


class SendingPayload(BotXType):
    text: Optional[str] = Schema(None, max_length=TEXT_MAX_LENGTH)
    file: Optional[File] = None
    markup: MessageMarkup = MessageMarkup()
    options: MessageOptions = MessageOptions()


class ErrorResponseData(BotXType):
    status_code: int
    body: str


class BotXAPIErrorData(BotXType):
    address: SendingCredentials
    response: ErrorResponseData
