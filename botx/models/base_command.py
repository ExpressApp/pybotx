from dataclasses import dataclass
from typing import Any, Dict, Optional
from uuid import UUID

from pydantic import validator

from botx.bot.api.constants import BOT_API_VERSION
from botx.bot.api.enums import BotAPIClientPlatforms, BotAPICommandTypes
from botx.bot.api.exceptions import UnsupportedBotAPIVersionError
from botx.shared_models.api_base import VerifiedPayloadBaseModel
from botx.shared_models.chat_types import APIChatTypes

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal  # type: ignore  # noqa: WPS440


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
    ad_domain: Optional[str]
    ad_login: Optional[str]
    username: Optional[str]
    is_admin: Optional[bool]
    is_creator: Optional[bool]


class BotAPIChatContext(BaseBotAPIContext):
    group_chat_id: UUID
    chat_type: APIChatTypes


class BotAPIDeviceContext(BaseBotAPIContext):
    app_version: Optional[str]
    platform: Optional[BotAPIClientPlatforms]
    platform_package_id: Optional[str]
    device: Optional[str]
    device_meta: BotAPIDeviceMeta
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


@dataclass
class BotCommandBase:
    bot_id: UUID
    raw_command: Optional[Dict[str, Any]]
