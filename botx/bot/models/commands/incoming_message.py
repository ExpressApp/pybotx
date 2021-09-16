from dataclasses import dataclass
from typing import Any, Dict, Optional
from uuid import UUID

from botx.bot.models.commands.base import BotCommandBase
from botx.bot.models.commands.enums import ChatTypes, ClientPlatforms


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
class Chat:
    id: UUID
    bot_id: UUID
    type: ChatTypes
    host: str


@dataclass
class IncomingMessage(BotCommandBase):
    sync_id: UUID
    source_sync_id: Optional[UUID]
    body: str
    data: Dict[str, Any]
    metadata: Dict[str, Any]
    sender: UserEventSender
    chat: Chat
