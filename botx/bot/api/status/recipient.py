from typing import Optional
from uuid import UUID

from botx.bot.models.status.recipient import StatusRecipient
from botx.shared_models.api_base import APIBaseModel
from botx.shared_models.enums import APIChatTypes, convert_chat_type_to_domain


class BotAPIStatusRecipient(APIBaseModel):
    bot_id: UUID
    user_huid: UUID
    ad_login: Optional[str]
    ad_domain: Optional[str]
    is_admin: Optional[bool]
    chat_type: APIChatTypes

    def to_domain(self) -> StatusRecipient:
        return StatusRecipient(
            bot_id=self.bot_id,
            huid=self.user_huid,
            ad_login=self.ad_login,
            ad_domain=self.ad_domain,
            is_admin=bool(self.is_admin),
            chat_type=convert_chat_type_to_domain(self.chat_type),
        )
