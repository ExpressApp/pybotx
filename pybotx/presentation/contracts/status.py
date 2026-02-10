from dataclasses import asdict, dataclass
from typing import Any, Literal
from uuid import UUID

from pydantic import field_validator

from pybotx.presentation.contracts.api_base import VerifiedPayloadBaseModel
from pybotx.presentation.contracts.enums import APIChatTypes, convert_chat_type_to_domain
from pybotx.domain.models.status import BotMenu, StatusRecipient


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
