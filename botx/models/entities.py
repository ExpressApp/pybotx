"""Entities that can be received in message."""

from datetime import datetime
from typing import Dict, List, Optional, Union, cast
from uuid import UUID, uuid4

from pydantic import Field, validator

from botx.models.attachments_meta import AttachmentMeta
from botx.models.base import BotXBaseModel
from botx.models.enums import ChatTypes, EntityTypes, MentionTypes


class Forward(BotXBaseModel):
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
    source_sync_id: UUID

    #: id of event creation.
    source_inserted_at: datetime


class UserMention(BotXBaseModel):
    """Mention for single user in chat or by `user_huid`."""

    #: huid of user that will be mentioned.
    user_huid: UUID

    #: name that will be used instead of default user name.
    name: Optional[str] = None

    #: connection type via that entity was mention
    conn_type: Optional[str] = None


class ChatMention(BotXBaseModel):
    """Mention chat in message by `group_chat_id`."""

    #: id of chat that will be mentioned.
    group_chat_id: UUID

    #: name that will be used instead of default chat name.
    name: Optional[str] = None


class Mention(BotXBaseModel):
    """Mention that is used in bot in messages."""

    #: unique id of mention.
    mention_id: Optional[UUID] = None

    #: information about mention object
    mention_data: Optional[Union[ChatMention, UserMention, Dict]]

    #: payload with data about mention.
    mention_type: MentionTypes = MentionTypes.user

    @validator("mention_id", pre=True, always=True)
    def generate_mention_id(cls, mention_id: Optional[UUID]) -> UUID:  # noqa: N805
        """Verify that `mention_id` will be in mention.

        Arguments:
            mention_id: id that should present or new UUID4 will be generated.

        Returns:
             Mention ID.
        """
        return mention_id or uuid4()

    @validator("mention_data", pre=True, always=True)
    def ignore_empty_data(
        cls,
        mention_data: Union[ChatMention, UserMention, Dict],  # noqa: N805
    ) -> Optional[Union[ChatMention, UserMention, Dict]]:
        """Pass empty dict into mention_data as None.

        Arguments:
            mention_data: dict of mention's data.

        Returns:
             Mention's data if is not empty or None.
        """
        if mention_data == {}:  # noqa: WPS520
            return None

        return mention_data

    @validator("mention_type", pre=True, always=True)
    def check_that_type_matches_data(  # noqa: WPS231, WPS210
        cls,
        mention_type: MentionTypes,
        values: dict,  # noqa: N805, WPS110
    ) -> MentionTypes:
        """Verify that `mention_type` matches provided `mention_data`.

        Arguments:
            mention_type: mention type that should be consistent with data.
            values: verified data.

        Returns:
            Checked mention type.

        Raises:
            ValueError: raised if mention_type does not corresponds with data.
        """
        mention_data = values.get("mention_data")
        if (mention_type != MentionTypes.all_members) and (mention_data is None):
            raise ValueError("no `mention_data`, perhaps this entity isn't a mention")

        user_mention_types = {MentionTypes.user, MentionTypes.contact}
        chat_mention_types = {MentionTypes.chat, MentionTypes.channel}

        is_user_mention_signature = isinstance(mention_data, UserMention) and (
            mention_type in user_mention_types
        )
        is_chat_mention_signature = isinstance(mention_data, ChatMention) and (
            mention_type in chat_mention_types
        )
        is_mention_all_signature = mention_type == MentionTypes.all_members

        if not any(  # noqa: WPS337
            {
                is_chat_mention_signature,
                is_mention_all_signature,
                is_user_mention_signature,
            },
        ):
            raise ValueError("No one suitable type for this mention_data signature")

        return mention_type

    @classmethod
    def build_from_values(
        cls,
        mention_type: MentionTypes,
        mentioned_entity_id: UUID,
        name: Optional[str] = None,
        mention_id: Optional[UUID] = None,
    ) -> "Mention":
        """Build mention.

        Simpler to use than constructor 'cause of flat values.

        Arguments:
            mention_type: mention type.
            mentioned_entity_id: id of mentioned entity (user, chat, etc.).
            name: for overriding mention name.
            mention_id: mention id (if not passed, will be generated).

        Raises:
            NotImplementedError: If unsupported mention type was passed.

        Returns:
            Built mention.
        """
        mention_data: Union[UserMention, ChatMention]

        if mention_type in {MentionTypes.user, MentionTypes.contact}:
            mention_data = UserMention(user_huid=mentioned_entity_id, name=name)
        elif mention_type in {MentionTypes.chat, MentionTypes.channel}:
            mention_data = ChatMention(group_chat_id=mentioned_entity_id, name=name)
        else:
            raise NotImplementedError("Unsupported mention type")

        return cls(
            mention_id=mention_id,
            mention_data=mention_data,
            mention_type=mention_type,
        )

    def to_botx_format(self) -> str:
        """Format mention to format, which can be parse by botx.

        Raises:
            NotImplementedError: If unsupported mention type was passed.

        Returns:
            Formatted mention.
        """
        formatted_mention_data = "{{mention:{0}}}".format(self.mention_id)

        if self.mention_type == MentionTypes.user:
            prefix = "@"
        elif self.mention_type == MentionTypes.contact:
            prefix = "@@"
        elif self.mention_type in {MentionTypes.chat, MentionTypes.channel}:
            prefix = "##"
        else:
            raise NotImplementedError("Unsupported mention type")

        return "{0}{1}".format(prefix, formatted_mention_data)


class Reply(BotXBaseModel):
    """Message that was replied."""

    #: attachment metadata.
    attachment_meta: Optional[AttachmentMeta] = Field(alias="attachment")

    #: text of source message.
    body: Optional[str]

    #: mentions of source message.
    mentions: List[Mention] = []

    #: type of source message's chat.
    reply_type: ChatTypes

    #: uuid of sender.
    sender: UUID

    #: chat name of source message.
    source_chat_name: Optional[str]

    #: chat uuid of source message.
    source_group_chat_id: Optional[UUID]

    #: uuid of source message.
    source_sync_id: UUID

    class Config:
        allow_population_by_field_name = True


class Entity(BotXBaseModel):
    """Additional entity that can be received by bot."""

    #: entity type.
    type: EntityTypes  # noqa: WPS125

    #: entity data.
    data: Union[Forward, Mention, Reply]  # noqa: WPS110


class EntityList(BotXBaseModel):
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
