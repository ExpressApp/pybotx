from typing import Any, Dict, Optional
from uuid import UUID

from pydantic import validator

from botx.shared_models.api_base import APIBaseModel
from botx.bot.api.constants import BOT_API_VERSION
from botx.bot.api.enums import BotAPIClientPlatforms, BotAPICommandTypes
from botx.bot.api.exceptions import UnsupportedBotAPIVersionError
from botx.shared_models.enums import APIChatTypes

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal  # type: ignore  # noqa: WPS440


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


class BotAPIServerEventSender(BotAPIBaseSender):
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
    proto_version: int

    @validator("proto_version", pre=True)
    @classmethod
    def validate_proto_version(cls, version: Any) -> int:
        if isinstance(version, int) and version == BOT_API_VERSION:
            return version

        raise UnsupportedBotAPIVersionError(version)
