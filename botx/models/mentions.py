"""Pydantic models for mentions."""

from enum import Enum
from typing import Optional, Union
from uuid import UUID, uuid4

from pydantic import BaseModel, validator


class MentionTypes(str, Enum):  # noqa: WPS600
    """Enum for available values in mentions."""

    user = "user"
    """mention single user from chat in message."""
    contact = "contact"
    """mention user by user_huid."""
    chat = "chat"
    """mention chat in message."""
    channel = "channel"
    """mention channel in message."""


class UserMention(BaseModel):
    """Mention for single user in chat or by `user_huid`."""

    user_huid: UUID
    """huid of user that will be mentioned."""
    name: Optional[str] = None
    """name that will be used instead of default user name."""


class ChatMention(BaseModel):
    """Mention chat in message by `group_chat_id`."""

    group_chat_id: UUID
    """id of chat that will be mentioned."""
    name: Optional[str] = None
    """name that will be used instead of default chat name."""


class Mention(BaseModel):
    """Mention that is used in bot in messages."""

    mention_id: Optional[UUID] = None
    """unique id of mention."""
    mention_data: Union[ChatMention, UserMention]
    """mention type."""
    mention_type: MentionTypes = MentionTypes.user
    """payload with data about mention."""

    @validator("mention_id", pre=True, always=True)
    def generate_mention_id(cls, mention_id: Optional[UUID]) -> UUID:  # noqa: N805
        """Verify that `mention_id` will be in mention.

        Arguments:
            mention_id: id that should present or new UUID4 will be generated.

        Returns:
             Mention ID.
        """
        return mention_id or uuid4()

    @validator("mention_type", pre=True, always=True)
    def check_that_type_matches_data(
        cls, mention_type: MentionTypes, values: dict  # noqa: N805
    ) -> MentionTypes:
        """Verify that `mention_type` matches provided `mention_data`.

        Arguments:
            mention_type: mention type that should be consistent with data.
            values: verified data.

        Returns:
            Checked mention type.
        """
        mention_data = values["mention_data"]
        user_mention_types = {MentionTypes.user, MentionTypes.contact}
        chat_mention_types = {MentionTypes.chat, MentionTypes.channel}

        if isinstance(mention_data, UserMention):
            if mention_type in user_mention_types:
                return mention_type
            raise ValueError(
                "mention_type for provided mention_data is wrong, accepted: {0}",
                user_mention_types,
            )

        if mention_type in chat_mention_types:
            return mention_type
        raise ValueError(
            "mention_type for provided mention_data is wrong, accepted: {0}",
            chat_mention_types,
        )
