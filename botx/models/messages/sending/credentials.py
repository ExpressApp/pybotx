"""Definition for sending credentials."""

from typing import Optional
from uuid import UUID

from pydantic import BaseModel, validator


class SendingCredentials(BaseModel):
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

    @validator("chat_id", always=True)
    def receiver_id_should_be_passed(
        cls, chat_id: Optional[UUID], values: dict,  # noqa: N805, WPS110
    ) -> Optional[UUID]:
        """Check that `chat_id` or `sync_id` was passed.

        Arguments:
            cls: this class.
            chat_id: value that should be checked.
            values: all other validated_values checked before.

        Raises:
            ValueError: raised if no value that can be used as received ID was passed.

        Returns:
            ID of chat if passed.
        """
        if not (chat_id or values["sync_id"]):
            raise ValueError(
                "sync_id, chat_id or chat_ids should be passed to initialization",
            )

        return chat_id
