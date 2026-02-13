from dataclasses import dataclass
from typing import Any, Literal
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
    data: dict[str, Any]
    metadata: dict[str, Any]


class BotAPIDeviceMeta(VerifiedPayloadBaseModel):
    pushes: bool | None = None
    timezone: str | None = None
    permissions: dict[str, Any] | None = None


class BaseBotAPIContext(VerifiedPayloadBaseModel):
    host: str


class BotAPIUserContext(BaseBotAPIContext):
    user_huid: UUID
    user_udid: UUID | None = None
    ad_domain: str | None = None
    ad_login: str | None = None
    username: str | None = None
    is_admin: bool | None = None
    is_creator: bool | None = None


class BotAPIChatContext(BaseBotAPIContext):
    group_chat_id: UUID
    chat_type: APIChatTypes | str


class BotAPIDeviceContext(BaseBotAPIContext):
    app_version: str | None = None
    platform: BotAPIClientPlatforms | None = None
    platform_package_id: str | None = None
    device: str | None = None
    device_meta: BotAPIDeviceMeta | None = None
    device_software: str | None = None
    manufacturer: str | None = None
    locale: str | None = None


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


@dataclass(slots=True)
class BotCommandBase:
    bot: BotAccount
    raw_command: dict[str, Any] | None
