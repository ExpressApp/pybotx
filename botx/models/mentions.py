"""Pydantic models for mentions."""

from typing import Optional, Union
from uuid import UUID, uuid4

from pydantic import BaseModel, validator

from botx.models.enums import MentionTypes


class UserMention(BaseModel):
    """Mention for single user in chat or by `user_huid`."""

    #: huid of user that will be mentioned.
    user_huid: UUID

    #: name that will be used instead of default user name.
    name: Optional[str] = None


class ChatMention(BaseModel):
    """Mention chat in message by `group_chat_id`."""

    #: id of chat that will be mentioned.
    group_chat_id: UUID

    #: name that will be used instead of default chat name.
    name: Optional[str] = None


class Mention(BaseModel):
    """Mention that is used in bot in messages."""

    #: unique id of mention.
    mention_id: Optional[UUID] = None

    #: mention type.
    mention_data: Union[ChatMention, UserMention]

    #: payload with data about mention.
    mention_type: MentionTypes = MentionTypes.user

    @validator("mention_id", pre=True, always=True)
    def generate_mention_id(cls, mention_id: Optional[UUID]) -> UUID:  # noqa: N805
        """Verify that `mention_id` will be in mention.

        Arguments:
            cls: this class.
            mention_id: id that should present or new UUID4 will be generated.

        Returns:
             Mention ID.
        """
        return mention_id or uuid4()

    @validator("mention_type", pre=True, always=True)
    def check_that_type_matches_data(
        cls, mention_type: MentionTypes, values: dict,  # noqa: N805, WPS110
    ) -> MentionTypes:
        """Verify that `mention_type` matches provided `mention_data`.

        Arguments:
            cls: this class.
            mention_type: mention type that should be consistent with data.
            values: verified data.

        Returns:
            Checked mention type.

        Raises:
            ValueError: raised if mention_type does not corresponds with data.
        """
        mention_data = values.get("mention_data")
        if mention_data is None:
            raise ValueError("no `mention_data`, perhaps this entity isn't a mention")

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
