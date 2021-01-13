"""Definition for sending credentials."""

from typing import Optional
from uuid import UUID

from botx.models.base import BotXBaseModel


class SendingCredentials(BotXBaseModel):
    """Credentials that are required to send command or notification result."""

    #: message event id.
    sync_id: Optional[UUID] = None

    #: id of message that will be sent.
    message_id: Optional[UUID] = None

    #: chat id in which bot should send message.
    chat_id: Optional[UUID] = None

    #: bot that handles message.
    bot_id: Optional[UUID] = None

    #: host on which bot answers.
    host: Optional[str] = None

    #: token that is used for bot authorization on requests to BotX API.
    token: Optional[str] = None
