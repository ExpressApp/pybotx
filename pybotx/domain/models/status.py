from dataclasses import dataclass
from typing import NewType
from uuid import UUID

from pybotx.domain.models.enums import IncomingChatTypes
from pybotx.domain.models.message.incoming_message import IncomingMessage

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
