from dataclasses import dataclass
from typing import Any, Dict, Literal, Optional, Union
from uuid import UUID

from pybotx.bot.api.exceptions import (
    UnknownSystemEventError,
    UnsupportedBotAPIVersionError,
)
from pybotx.constants import BOT_API_VERSION
from pybotx.models.api_base import VerifiedPayloadBaseModel
from pybotx.models.bot_account import BotAccount
from pybotx.models.enums import (
    APIChatTypes,
    BotAPIClientPlatforms,
    BotAPICommandTypes,
    BotAPISystemEventTypes,
)
from pydantic import field_validator


class BotAPICommandPayload(VerifiedPayloadBaseModel):
    body: str
    command_type: Literal[BotAPICommandTypes.USER]
    data: Dict[str, Any]
    metadata: Dict[str, Any]


class BotAPIDeviceMeta(VerifiedPayloadBaseModel):
    pushes: Optional[bool] = None
    timezone: Optional[str] = None
    permissions: Optional[Dict[str, Any]] = None


class BaseBotAPIContext(VerifiedPayloadBaseModel):
    host: str


class BotAPIUserContext(BaseBotAPIContext):
    user_huid: UUID
    user_udid: Optional[UUID] = None
    ad_domain: Optional[str] = None
    ad_login: Optional[str] = None
    username: Optional[str] = None
    is_admin: Optional[bool] = None
    is_creator: Optional[bool] = None


class BotAPIChatContext(BaseBotAPIContext):
    group_chat_id: UUID
    chat_type: Union[APIChatTypes, str]


class BotAPIDeviceContext(BaseBotAPIContext):
    app_version: Optional[str] = None
    platform: Optional[BotAPIClientPlatforms] = None
    platform_package_id: Optional[str] = None
    device: Optional[str] = None
    device_meta: Optional[BotAPIDeviceMeta] = None
    device_software: Optional[str] = None
    manufacturer: Optional[str] = None
    locale: Optional[str] = None


class BotAPIBaseCommand(VerifiedPayloadBaseModel):
    bot_id: UUID
    sync_id: UUID
    proto_version: int

    @field_validator("proto_version", mode="before")
    @classmethod
    def validate_proto_version(cls, version: Any) -> int:
        if isinstance(version, int) and version == BOT_API_VERSION:
            return version

        raise UnsupportedBotAPIVersionError(version)


class BotAPIBaseSystemEventPayload(VerifiedPayloadBaseModel):
    command_type: Literal[BotAPICommandTypes.SYSTEM]

    @field_validator("body", mode="before", check_fields=False)
    @classmethod
    def find_unknown_system_event(cls, body: str) -> str:
        if body not in BotAPISystemEventTypes.__members__.values():
            raise UnknownSystemEventError(body)

        return body


@dataclass
class BotCommandBase:
    bot: BotAccount
    raw_command: Optional[Dict[str, Any]]
