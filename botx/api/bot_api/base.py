from typing import Any, Dict, Literal, Optional
from uuid import UUID

from botx.api.bot_api.enums import BotAPIClientPlatforms, BotAPICommandTypes
from botx.api.enums import APIChatTypes
from botx.api.pydantic import APIBaseModel


class BotAPICommandPayload(APIBaseModel):
    body: str
    command_type: Literal[BotAPICommandTypes.USER]
    data: Dict[str, Any]
    metadata: Dict[str, Any]


class BotAPIDeviceMeta(APIBaseModel):
    pushes: Optional[bool]
    timezone: Optional[str]
    permissions: Optional[Dict[str, Any]]


class BotAPIBaseSender(APIBaseModel):
    ad_domain: Optional[str]
    ad_login: Optional[str]
    app_version: Optional[str]
    device: Optional[str]
    device_meta: BotAPIDeviceMeta
    device_software: Optional[str]
    host: str
    locale: Optional[str]
    manufacturer: Optional[str]
    platform: Optional[BotAPIClientPlatforms]
    platform_package_id: Optional[str]
    username: Optional[str]


class BotAPISystemEventSender(BotAPIBaseSender):
    is_admin: Literal[None]
    is_creator: Literal[None]
    chat_type: Optional[APIChatTypes]
    group_chat_id: Optional[UUID]
    user_huid: Optional[UUID]


class BotAPIChatEventSender(BotAPIBaseSender):
    is_admin: Literal[None]
    is_creator: Literal[None]
    chat_type: APIChatTypes
    group_chat_id: UUID
    user_huid: Optional[UUID]


class BotAPIUserEventSender(BotAPIBaseSender):
    is_admin: bool
    is_creator: bool
    chat_type: APIChatTypes
    group_chat_id: UUID
    user_huid: UUID


class BotAPIBaseCommand(APIBaseModel):
    bot_id: UUID
    sync_id: UUID
