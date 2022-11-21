from dataclasses import dataclass
from typing import Any, Dict, Literal

from pydantic import Field

from pybotx.models.api_base import VerifiedPayloadBaseModel
from pybotx.models.base_command import (
    BotAPIBaseCommand,
    BotAPIBaseSystemEventPayload,
    BotAPIChatContext,
    BotAPIUserContext,
    BotCommandBase,
)
from pybotx.models.bot_account import BotAccount
from pybotx.models.bot_sender import BotSender
from pybotx.models.chats import Chat
from pybotx.models.enums import BotAPISystemEventTypes, convert_chat_type_to_domain


@dataclass
class InternalBotNotificationEvent(BotCommandBase):
    """Event `system:internal_bot_notification`.

    Attributes:
        data: user data.
        opts: request options.
    """

    data: Dict[str, Any]
    opts: Dict[str, Any]
    chat: Chat
    sender: BotSender


class BotAPIInternalBotNotificationData(VerifiedPayloadBaseModel):
    data: Dict[str, Any]
    opts: Dict[str, Any]


class BotAPIInternalBotNotificationPayload(BotAPIBaseSystemEventPayload):
    body: Literal[BotAPISystemEventTypes.INTERNAL_BOT_NOTIFICATION]
    data: BotAPIInternalBotNotificationData


class BotAPIBotContext(BotAPIChatContext, BotAPIUserContext):
    """Bot context."""


class BotAPIInternalBotNotification(BotAPIBaseCommand):
    payload: BotAPIInternalBotNotificationPayload = Field(..., alias="command")
    sender: BotAPIBotContext = Field(..., alias="from")

    def to_domain(self, raw_command: Dict[str, Any]) -> InternalBotNotificationEvent:
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
