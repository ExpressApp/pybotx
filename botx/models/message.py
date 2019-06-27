from typing import (
    TYPE_CHECKING,
    Any,
    BinaryIO,
    Dict,
    List,
    Optional,
    TextIO,
    Type,
    TypeVar,
    Union,
    cast,
)
from uuid import UUID

from pydantic import Schema

from botx.core import TEXT_MAX_LENGTH

from .base import BotXType
from .common import NotificationOpts, SyncID
from .enums import ChatTypeEnum, ResponseRecipientsEnum
from .file import File
from .mention import Mention, MentionUser
from .ui import BubbleElement, KeyboardElement

if TYPE_CHECKING:  # pragma: no cover
    from .ui import UIElement

    TUIElement = TypeVar("TUIElement", bound=UIElement)


class MessageUser(BotXType):
    user_huid: Optional[UUID]
    group_chat_id: UUID
    chat_type: ChatTypeEnum
    ad_login: Optional[str]
    ad_domain: Optional[str]
    username: Optional[str]
    host: str

    @property
    def email(self) -> Optional[str]:
        if self.ad_login and self.ad_domain:
            return f"{self.ad_login}@{self.ad_domain}"

        return None


class MessageCommand(BotXType):
    body: str
    data: Dict[str, Any] = {}

    @property
    def command(self) -> str:
        return self.body.split(" ", 1)[0]

    @property
    def arguments(self) -> List[str]:
        return [arg for arg in self.body.split(" ")[1:] if arg and not arg.isspace()]

    @property
    def single_argument(self) -> str:
        arg_in_list = self.body.split(" ", 1)[1:]
        return arg_in_list[0] if arg_in_list else ""


class Message(BotXType):
    sync_id: SyncID
    command: MessageCommand
    file: Optional[File] = None
    user: MessageUser = Schema(..., alias="from")  # type: ignore
    bot_id: UUID

    def __init__(self, **data: Dict[str, Any]) -> None:
        super().__init__(**data)

        self.sync_id = SyncID(self.sync_id)

    @property
    def body(self) -> str:
        return self.command.body

    @property
    def data(self) -> Dict[str, Any]:
        return self.command.data

    @property
    def user_huid(self) -> Optional[UUID]:
        return self.user.user_huid

    @property
    def ad_login(self) -> Optional[str]:
        return self.user.ad_login

    @property
    def group_chat_id(self) -> UUID:
        return self.user.group_chat_id

    @property
    def chat_type(self) -> str:
        return self.user.chat_type.name

    @property
    def host(self) -> str:
        return self.user.host


def _add_ui_element(
    ui_cls: Type["TUIElement"],
    ui_array: List[List["TUIElement"]],
    command: str,
    label: Optional[str] = None,
    *,
    data: Optional[Dict[str, Any]] = None,
    new_row: bool = True,
) -> None:
    data = data or {}

    element = ui_cls(command=command, label=label, data=data)

    if new_row:
        ui_array.append([element])
    else:
        ui_array[-1].append(element)


class ReplyMessage(BotXType):
    text: str = Schema(..., max_length=TEXT_MAX_LENGTH)  # type: ignore
    chat_id: Union[SyncID, UUID, List[UUID]]
    bot_id: UUID
    host: str
    recipients: Union[List[UUID], str] = ResponseRecipientsEnum.all
    mentions: List[Mention] = []
    bubble: List[List[BubbleElement]] = []
    keyboard: List[List[KeyboardElement]] = []
    opts: NotificationOpts = NotificationOpts()
    file: Optional[File] = None

    @classmethod
    def from_message(cls, text: str, message: Message) -> "ReplyMessage":
        reply_msg = cls(
            text=text, chat_id=message.sync_id, bot_id=message.bot_id, host=message.host
        )
        return reply_msg

    def add_file(self, file: Union[TextIO, BinaryIO]) -> None:
        self.file = File.from_file(file)

    def mention_user(self, user_huid: UUID, name: Optional[str] = None) -> None:
        self.mentions.append(
            Mention(mention_data=MentionUser(user_huid=user_huid, name=name))
        )

    def add_recipient(self, recipient: UUID) -> None:
        if self.recipients == ResponseRecipientsEnum.all:
            self.recipients = []

        cast(List[UUID], self.recipients).append(recipient)

    def add_recipients(self, recipients: List[UUID]) -> None:
        if self.recipients == ResponseRecipientsEnum.all:
            self.recipients = []

        cast(List[UUID], self.recipients).extend(recipients)

    def add_bubble(
        self,
        command: str,
        label: Optional[str] = None,
        *,
        data: Optional[Dict[str, Any]] = None,
        new_row: bool = True,
    ) -> None:
        _add_ui_element(
            ui_cls=BubbleElement,
            ui_array=self.bubble,
            command=command,
            label=label,
            data=data,
            new_row=new_row,
        )

    def add_keyboard_button(
        self,
        command: str,
        label: Optional[str] = None,
        *,
        data: Optional[Dict[str, Any]] = None,
        new_row: bool = True,
    ) -> None:
        _add_ui_element(
            ui_cls=KeyboardElement,
            ui_array=self.keyboard,
            command=command,
            label=label,
            data=data,
            new_row=new_row,
        )

    def show_notification(self, show: bool) -> None:
        self.opts.send = show

    def force_notification(self, force: bool) -> None:
        self.opts.force_dnd = force
