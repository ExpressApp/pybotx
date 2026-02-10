from dataclasses import dataclass
from typing import Any

from pybotx.domain.models.base_command import BotCommandBase
from pybotx.domain.models.bot_sender import BotSender
from pybotx.domain.models.chats import Chat


@dataclass(slots=True)
class InternalBotNotificationEvent(BotCommandBase):
    """Event `system:internal_bot_notification`.

    Attributes:
        data: user data.
        opts: request options.
    """

    data: dict[str, Any]
    opts: dict[str, Any]
    chat: Chat
    sender: BotSender
