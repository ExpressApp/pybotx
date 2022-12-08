from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Literal, NewType, Optional, Union
from uuid import UUID

from pydantic import validator

from pybotx.models.api_base import VerifiedPayloadBaseModel
from pybotx.models.enums import (
    APIChatTypes,
    IncomingChatTypes,
    convert_chat_type_to_domain,
)
from pybotx.models.message.incoming_message import IncomingMessage

BotMenu = NewType("BotMenu", Dict[str, str])


@dataclass
class StatusRecipient:
    bot_id: UUID
    huid: UUID
    ad_login: Optional[str]
    ad_domain: Optional[str]
    is_admin: Optional[bool]
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
    ad_login: Optional[str]
    ad_domain: Optional[str]
    is_admin: Optional[bool]
    chat_type: Union[APIChatTypes, str]

    @validator("ad_login", "ad_domain", "is_admin", pre=True)
    @classmethod
    def replace_empty_string(
        cls,
        field_value: Union[str, bool],
    ) -> Union[str, bool, None]:
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


@dataclass
class BotAPIBotMenuItem:
    description: str
    body: str
    name: str


BotAPIBotMenu = List[BotAPIBotMenuItem]


@dataclass
class BotAPIStatusResult:
    commands: BotAPIBotMenu
    enabled: Literal[True] = True
    status_message: Optional[str] = None


@dataclass
class BotAPIStatus:
    result: BotAPIStatusResult
    status: Literal["ok"] = "ok"


def build_bot_status_response(bot_menu: BotMenu) -> Dict[str, Any]:
    commands = [
        BotAPIBotMenuItem(body=command, name=command, description=description)
        for command, description in bot_menu.items()
    ]

    status = BotAPIStatus(
        result=BotAPIStatusResult(status_message="Bot is working", commands=commands),
    )
    return asdict(status)
