from dataclasses import dataclass
from typing import Any, Dict, Literal, Optional, Union
from uuid import UUID

from pydantic import validator

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


class BotAPICommandPayload(VerifiedPayloadBaseModel):
    body: str
    command_type: Literal[BotAPICommandTypes.USER]
    data: Dict[str, Any]
    metadata: Dict[str, Any]


class BotAPIDeviceMeta(VerifiedPayloadBaseModel):
    pushes: Optional[bool]
    timezone: Optional[str]
    permissions: Optional[Dict[str, Any]]


class BaseBotAPIContext(VerifiedPayloadBaseModel):
    host: str


class BotAPIUserContext(BaseBotAPIContext):
    user_huid: UUID
    user_udid: Optional[UUID]
    ad_domain: Optional[str]
    ad_login: Optional[str]
    username: Optional[str]
    is_admin: Optional[bool]
    is_creator: Optional[bool]


class BotAPIChatContext(BaseBotAPIContext):
    group_chat_id: UUID
    chat_type: Union[APIChatTypes, str]


class BotAPIDeviceContext(BaseBotAPIContext):
    app_version: Optional[str]
    platform: Optional[BotAPIClientPlatforms]
    platform_package_id: Optional[str]
    device: Optional[str]
    device_meta: Optional[BotAPIDeviceMeta]
    device_software: Optional[str]
    manufacturer: Optional[str]
    locale: Optional[str]


class BotAPIBaseCommand(VerifiedPayloadBaseModel):
    bot_id: UUID
    sync_id: UUID
    proto_version: int

    @validator("proto_version", pre=True)
    @classmethod
    def validate_proto_version(cls, version: Any) -> int:
        if isinstance(version, int) and version == BOT_API_VERSION:
            return version

        raise UnsupportedBotAPIVersionError(version)


class BotAPIBaseSystemEventPayload(VerifiedPayloadBaseModel):
    command_type: Literal[BotAPICommandTypes.SYSTEM]

    @validator("body", pre=True, check_fields=False)
    @classmethod
    def find_unknown_system_event(cls, body: str) -> str:
        if body not in BotAPISystemEventTypes.__members__.values():  # noqa: WPS609
            raise UnknownSystemEventError(body)

        return body


@dataclass
class BotCommandBase:
    bot: BotAccount
    raw_command: Optional[Dict[str, Any]]
