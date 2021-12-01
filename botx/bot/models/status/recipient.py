from dataclasses import dataclass
from typing import Optional
from uuid import UUID

from botx.bot.models.commands.incoming_message import IncomingMessage
from botx.shared_models.chat_types import ChatTypes


@dataclass
class StatusRecipient:
    bot_id: UUID
    huid: UUID
    ad_login: Optional[str]
    ad_domain: Optional[str]
    is_admin: Optional[bool]
    chat_type: ChatTypes

    @classmethod
    def from_incoming_message(
        cls,
        incoming_message: IncomingMessage,
    ) -> "StatusRecipient":
        return StatusRecipient(
            bot_id=incoming_message.bot_id,
            huid=incoming_message.sender.huid,
            ad_login=incoming_message.sender.ad_login,
            ad_domain=incoming_message.sender.ad_domain,
            is_admin=incoming_message.sender.is_chat_admin,
            chat_type=incoming_message.chat.type,
        )
