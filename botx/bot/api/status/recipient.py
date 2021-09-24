from typing import Optional
from uuid import UUID

from botx.api_base_models import APIBaseModel
from botx.bot.api.enums import BotAPIChatTypes, convert_chat_type_to_domain
from botx.bot.models.status.recipient import StatusRecipient


class BotAPIStatusRecipient(APIBaseModel):
    bot_id: UUID
    user_huid: UUID
    ad_login: Optional[str]
    ad_domain: Optional[str]
    is_admin: Optional[bool]
    chat_type: BotAPIChatTypes

    def to_domain(self) -> StatusRecipient:
        return StatusRecipient(
            bot_id=self.bot_id,
            huid=self.user_huid,
            ad_login=self.ad_login,
            ad_domain=self.ad_domain,
            is_admin=bool(self.is_admin),
            chat_type=convert_chat_type_to_domain(self.chat_type),
        )
