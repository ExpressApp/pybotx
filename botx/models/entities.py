"""Entities that can be received in message."""

from datetime import datetime
from typing import List, Optional, Union, cast
from uuid import UUID, uuid4

from pydantic import BaseModel, validator

from botx.models.attachments import Attachments
from botx.models.enums import ChatTypes, EntityTypes, MentionTypes


class Forward(BaseModel):
    """Forward in message."""

    #: ID of chat from which forward received.
    group_chat_id: UUID

    #: ID of user that is author of message.
    sender_huid: UUID

    #: type of forward.
    forward_type: ChatTypes

    #: name of original chat.
    source_chat_name: Optional[str] = None

    #: id of original message event.
    source_sync_id: Optional[UUID]

    #: id of event creation.
    source_inserted_at: datetime


class UserMention(BaseModel):
    """Mention for single user in chat or by `user_huid`."""

    #: huid of user that will be mentioned.
    user_huid: UUID

    #: name that will be used instead of default user name.
    name: Optional[str] = None

    #: connection type via that entity was mention
    conn_type: Optional[str] = None


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


class Reply(BaseModel):
    """Message that was replied."""

    #: array of attachments.
    attachment: Optional[List[Attachments]] = []

    #: text of source message.
    body: str

    #: mentions of source message.
    mentions: List[Mention] = []

    #: type of source message's chat.
    reply_type: ChatTypes

    #: uuid of sender.
    sender: UUID

    #: chat name of source message.
    source_chat_name: str

    #: chat uuid of source message.
    source_group_chat_id: Optional[UUID]

    #: uuid of source message.
    source_sync_id: UUID


class Entity(BaseModel):
    """Additional entity that can be received by bot."""

    #: entity type.
    type: EntityTypes  # noqa: WPS125

    #: entity data.
    data: Union[Forward, Mention, Reply]  # noqa: WPS110


class EntityList(BaseModel):
    """Additional wrapped class for use property."""

    __root__: List[Entity]

    @property
    def mentions(self) -> List[Mention]:
        """Search mentions in message's entity.

        Returns:
            List of mentions.
        """
        return [
            cast(Mention, entity.data)
            for entity in self.__root__
            if entity.type == EntityTypes.mention
        ]

    @property
    def forward(self) -> Forward:
        """Search forward in message's entity.

        Returns:
            Information about forward.

        Raises:
            AttributeError: raised if message has no forward.
        """
        for entity in self.__root__:
            if entity.type == EntityTypes.forward:  # pragma: no branch
                return cast(Forward, entity.data)
        raise AttributeError("forward")

    @property
    def reply(self) -> Reply:
        """Search reply in message's entity.

        Returns:
            Reply.

        Raises:
            AttributeError: raised if message has no reply.
        """
        for entity in self.__root__:
            if entity.type == EntityTypes.reply:  # pragma: no branch
                return cast(Reply, entity.data)
        raise AttributeError("reply")
