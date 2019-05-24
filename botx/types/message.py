from typing import Any, Dict, Optional
from uuid import UUID

from pydantic import Schema

from .base import BotXType
from .core import SyncID
from .enums import ChatTypeEnum
from .file import File


class MessageUser(BotXType):
    user_huid: Optional[UUID]
    group_chat_id: UUID
    chat_type: ChatTypeEnum
    ad_login: Optional[str]
    ad_domain: Optional[str]
    username: Optional[str]
    host: str


class MessageCommand(BotXType):
    body: str
    data: Dict[str, Any] = {}

    @property
    def cmd(self) -> str:
        return self.body.split(" ", 1)[0]

    @property
    def cmd_arg(self) -> str:
        return "".join(self.body.split(" ", 1)[1:])


class Message(BotXType):
    sync_id: SyncID
    command: MessageCommand
    file: Optional[File] = None
    user: MessageUser = Schema(..., alias="from")  # type: ignore
    bot_id: UUID

    def __init__(self, **data):
        super().__init__(**data)

        self.sync_id = SyncID(data["sync_id"])

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
