from typing import Any, Literal

from pydantic import Field

from pybotx.presentation.contracts.api_base import VerifiedPayloadBaseModel
from pybotx.presentation.contracts.base_command import (
    BotAPIBaseCommand,
    BotAPIBaseSystemEventPayload,
    BotAPIChatContext,
    BotAPIUserContext,
)
from pybotx.presentation.contracts.enums import (
    BotAPISystemEventTypes,
    convert_chat_type_to_domain,
)
from pybotx.domain.models.bot_account import BotAccount
from pybotx.domain.models.bot_sender import BotSender
from pybotx.domain.models.chats import Chat
from pybotx.domain.models.system_events.internal_bot_notification import (
    InternalBotNotificationEvent,
)


class BotAPIInternalBotNotificationData(VerifiedPayloadBaseModel):
    data: dict[str, Any]
    opts: dict[str, Any]


class BotAPIInternalBotNotificationPayload(BotAPIBaseSystemEventPayload):
    body: Literal[BotAPISystemEventTypes.INTERNAL_BOT_NOTIFICATION]
    data: BotAPIInternalBotNotificationData


class BotAPIBotContext(BotAPIChatContext, BotAPIUserContext):
    """Bot context."""


class BotAPIInternalBotNotification(BotAPIBaseCommand):
    payload: BotAPIInternalBotNotificationPayload = Field(..., alias="command")
    sender: BotAPIBotContext = Field(..., alias="from")

    def to_domain(self, raw_command: dict[str, Any]) -> InternalBotNotificationEvent:
        return InternalBotNotificationEvent(
            bot=BotAccount(
                id=self.bot_id,
                host=self.sender.host,
            ),
            raw_command=raw_command,
            data=self.payload.data.data,
            opts=self.payload.data.opts,
            chat=Chat(
                id=self.sender.group_chat_id,
                type=convert_chat_type_to_domain(self.sender.chat_type),
            ),
            sender=BotSender(
                huid=self.sender.user_huid,
                is_chat_admin=self.sender.is_admin,
                is_chat_creator=self.sender.is_creator,
            ),
        )
