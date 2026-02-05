from dataclasses import asdict, dataclass
from typing import Any, Literal, NewType
from uuid import UUID

from pybotx.models.api_base import VerifiedPayloadBaseModel
from pybotx.models.enums import (
    APIChatTypes,
    IncomingChatTypes,
    convert_chat_type_to_domain,
)
from pybotx.models.message.incoming_message import IncomingMessage
from pydantic import field_validator

BotMenu = NewType("BotMenu", dict[str, str])


@dataclass(slots=True)
class StatusRecipient:
    bot_id: UUID
    huid: UUID
    ad_login: str | None
    ad_domain: str | None
    is_admin: bool | None
    chat_type: IncomingChatTypes

    @classmethod
    def from_incoming_message(
        cls,
        incoming_message: IncomingMessage,
    ) -> "StatusRecipient":
        return StatusRecipient(
            bot_id=incoming_message.bot.id,
            huid=incoming_message.sender.huid,
            ad_login=incoming_message.sender.ad_login,
            ad_domain=incoming_message.sender.ad_domain,
            is_admin=incoming_message.sender.is_chat_admin,
            chat_type=incoming_message.chat.type,
        )


class BotAPIStatusRecipient(VerifiedPayloadBaseModel):
    bot_id: UUID
    user_huid: UUID
    ad_login: str | None = None
    ad_domain: str | None = None
    is_admin: bool | None = None
    chat_type: APIChatTypes | str

    @field_validator("ad_login", "ad_domain", "is_admin", mode="before")
    @classmethod
    def replace_empty_string(
        cls,
        field_value: str | bool,
    ) -> str | bool | None:
        if field_value == "":
            return None

        return field_value

    def to_domain(self) -> StatusRecipient:
        return StatusRecipient(
            bot_id=self.bot_id,
            huid=self.user_huid,
            ad_login=self.ad_login,
            ad_domain=self.ad_domain,
            is_admin=self.is_admin,
            chat_type=convert_chat_type_to_domain(self.chat_type),
        )


@dataclass(slots=True)
class BotAPIBotMenuItem:
    description: str
    body: str
    name: str


BotAPIBotMenu = list[BotAPIBotMenuItem]


@dataclass(slots=True)
class BotAPIStatusResult:
    commands: BotAPIBotMenu
    enabled: Literal[True] = True
    status_message: str | None = None


@dataclass(slots=True)
class BotAPIStatus:
    result: BotAPIStatusResult
    status: Literal["ok"] = "ok"


def build_bot_status_response(bot_menu: BotMenu) -> dict[str, Any]:
    commands = [
        BotAPIBotMenuItem(body=command, name=command, description=description)
        for command, description in bot_menu.items()
    ]

    status = BotAPIStatus(
        result=BotAPIStatusResult(status_message="Bot is working", commands=commands),
    )
    return asdict(status)
