from dataclasses import dataclass, field
from types import SimpleNamespace
from typing import Any
from uuid import UUID

from pybotx.domain.models.attachments import (
    Contact,
    IncomingFileAttachment,
    Link,
    Location,
)
from pybotx.domain.models.base_command import BotCommandBase
from pybotx.domain.models.bot_account import BotAccount
from pybotx.domain.models.chats import Chat
from pybotx.domain.models.enums import ClientPlatforms
from pybotx.domain.models.message.forward import Forward
from pybotx.domain.models.message.mentions import Mention, MentionBuilder, MentionList
from pybotx.domain.models.message.reply import Reply
from pybotx.domain.models.stickers import Sticker


@dataclass(slots=True)
class UserDevice:
    manufacturer: str | None
    device_name: str | None
    os: str | None
    pushes: bool | None
    timezone: str | None
    permissions: dict[str, Any] | None
    platform: ClientPlatforms | None
    platform_package_id: str | None
    app_version: str | None
    locale: str | None


@dataclass(slots=True)
class UserSender:
    huid: UUID
    udid: UUID | None
    ad_login: str | None
    ad_domain: str | None
    username: str | None
    is_chat_admin: bool | None
    is_chat_creator: bool | None
    device: UserDevice

    @property
    def upn(self) -> str | None:
        # https://docs.microsoft.com/en-us/windows/win32/secauthn/user-name-formats
        if not (self.ad_login and self.ad_domain):
            return None

        return f"{self.ad_login}@{self.ad_domain}"


@dataclass(slots=True)
class IncomingMessage(BotCommandBase):
    sync_id: UUID
    source_sync_id: UUID | None
    body: str
    data: dict[str, Any]
    metadata: dict[str, Any]
    sender: UserSender
    chat: Chat
    mentions: MentionList = field(default_factory=MentionList)
    forward: Forward | None = None
    reply: Reply | None = None
    file: IncomingFileAttachment | None = None
    location: Location | None = None
    contact: Contact | None = None
    link: Link | None = None
    sticker: Sticker | None = None

    state: SimpleNamespace = field(default_factory=SimpleNamespace)

    @property
    def argument(self) -> str:
        split_body = self.body.split()
        if not split_body:
            return ""

        command_len = len(split_body[0])
        return self.body[command_len:].strip()

    @property
    def arguments(self) -> tuple[str, ...]:
        return tuple(arg.strip() for arg in self.argument.split())


Entity = Mention | Forward | Reply


__all__ = (
    "IncomingMessage",
    "UserDevice",
    "UserSender",
    "Entity",
    "Mention",
    "MentionBuilder",
    "MentionList",
    "BotAccount",
    "Chat",
)
