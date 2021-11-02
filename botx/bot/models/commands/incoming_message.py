from dataclasses import dataclass, field
from types import SimpleNamespace
from typing import Any, Dict, Optional, Union
from uuid import UUID

from botx.bot.models.commands.base import BotCommandBase
from botx.bot.models.commands.chat import Chat
from botx.bot.models.commands.enums import ClientPlatforms
from botx.shared_models.domain.attachments import (
    AttachmentContact,
    AttachmentLink,
    AttachmentLocation,
    IncomingFileAttachment,
)
from botx.shared_models.domain.files import File


@dataclass
class ExpressApp:
    pushes: Optional[bool]
    timezone: Optional[str]
    permissions: Optional[Dict[str, Any]]
    platform: Optional[ClientPlatforms]
    platform_package_id: Optional[str]
    version: Optional[str]


@dataclass
class UserDevice:
    manufacturer: Optional[str]
    name: Optional[str]
    os: Optional[str]


@dataclass
class UserEventSender:
    huid: UUID
    ad_login: Optional[str]
    ad_domain: Optional[str]
    username: Optional[str]
    is_chat_admin: bool
    is_chat_creator: bool
    locale: Optional[str]
    express_app: ExpressApp
    device: UserDevice

    @property
    def upn(self) -> Optional[str]:
        # https://docs.microsoft.com/en-us/windows/win32/secauthn/user-name-formats
        if not (self.ad_login and self.ad_domain):
            return None

        return f"{self.ad_login}@{self.ad_domain}"


@dataclass
class IncomingMessage(BotCommandBase):
    sync_id: UUID
    source_sync_id: Optional[UUID]
    body: str
    data: Dict[str, Any]
    metadata: Dict[str, Any]
    sender: UserEventSender
    chat: Chat
    file: Optional[Union[File, IncomingFileAttachment]] = None
    location: Optional[AttachmentLocation] = None
    contact: Optional[AttachmentContact] = None
    link: Optional[AttachmentLink] = None

    state: SimpleNamespace = field(default_factory=SimpleNamespace)
