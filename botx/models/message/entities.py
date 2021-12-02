from dataclasses import dataclass
from typing import Dict, List, Optional, Union, cast
from uuid import UUID

from pydantic import Field, validator

from botx.models.enums import (
    BotAPIEntityTypes,
    BotAPIMentionTypes,
    MentionTypes,
    convert_mention_type_to_domain,
)
from botx.shared_models.api_base import VerifiedPayloadBaseModel

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal  # type: ignore  # noqa: WPS440


@dataclass
class Mention:
    type: MentionTypes
    entity_id: Optional[UUID] = None
    name: Optional[str] = None

    def __str__(self) -> str:
        name = self.name or ""
        entity_id = self.entity_id or ""
        mention_type = self.type.value
        return f"<embed_mention>{mention_type}:{entity_id}:{name}</embed_mention>"

    @classmethod
    def user(cls, huid: UUID, name: Optional[str] = None) -> "Mention":
        return cls(
            type=MentionTypes.USER,
            entity_id=huid,
            name=name,
        )

    @classmethod
    def contact(cls, huid: UUID, name: Optional[str] = None) -> "Mention":
        return cls(
            type=MentionTypes.CONTACT,
            entity_id=huid,
            name=name,
        )

    @classmethod
    def chat(cls, chat_id: UUID, name: Optional[str] = None) -> "Mention":
        return cls(
            type=MentionTypes.CHAT,
            entity_id=chat_id,
            name=name,
        )

    @classmethod
    def channel(cls, chat_id: UUID, name: Optional[str] = None) -> "Mention":
        return cls(
            type=MentionTypes.CHANNEL,
            entity_id=chat_id,
            name=name,
        )

    @classmethod
    def all(cls) -> "Mention":
        return cls(type=MentionTypes.ALL)


class MentionList(List[Mention]):
    @property
    def contacts(self) -> List[Mention]:
        return [mention for mention in self if mention.type == MentionTypes.CONTACT]

    @property
    def chats(self) -> List[Mention]:
        return [mention for mention in self if mention.type == MentionTypes.CHAT]

    @property
    def channels(self) -> List[Mention]:
        return [mention for mention in self if mention.type == MentionTypes.CHANNEL]

    @property
    def users(self) -> List[Mention]:
        return [mention for mention in self if mention.type == MentionTypes.USER]

    @property
    def all_users_mentioned(self) -> bool:
        for mention in self:
            if mention.type == MentionTypes.ALL:
                return True

        return False


@dataclass
class Forward:
    chat_id: UUID
    author_id: UUID
    sync_id: UUID


@dataclass
class Reply:
    author_id: UUID
    sync_id: UUID
    body: str
    mentions: MentionList


Entity = Union[Mention, Forward, Reply]


class BotAPINestedPersonalMentionData(VerifiedPayloadBaseModel):
    entity_id: UUID = Field(alias="user_huid")
    name: str
    conn_type: str


class BotAPINestedGroupMentionData(VerifiedPayloadBaseModel):
    entity_id: UUID = Field(alias="group_chat_id")
    name: str


BotAPINestedMentionData = Union[
    BotAPINestedPersonalMentionData,
    BotAPINestedGroupMentionData,
]


class BotAPIMentionData(VerifiedPayloadBaseModel):
    mention_type: BotAPIMentionTypes
    mention_id: UUID
    mention_data: Optional[BotAPINestedMentionData]

    @validator("mention_data", pre=True)
    @classmethod
    def validate_mention_data(
        cls,
        mention_data: Dict[str, str],
    ) -> Optional[Dict[str, str]]:
        # Mention data can be an empty dict
        if not mention_data:
            return None

        return mention_data


class BotAPIMention(VerifiedPayloadBaseModel):
    type: Literal[BotAPIEntityTypes.MENTION]
    data: BotAPIMentionData


class BotAPIForwardData(VerifiedPayloadBaseModel):
    group_chat_id: UUID
    sender_huid: UUID
    source_sync_id: UUID


class BotAPIForward(VerifiedPayloadBaseModel):
    type: Literal[BotAPIEntityTypes.FORWARD]
    data: BotAPIForwardData


class BotAPIReplyData(VerifiedPayloadBaseModel):
    source_sync_id: UUID
    sender: UUID
    body: str
    mentions: List[BotAPIMentionData]
    # Ignoring attachments cause they don't have content


class BotAPIReply(VerifiedPayloadBaseModel):
    type: Literal[BotAPIEntityTypes.REPLY]
    data: BotAPIReplyData


BotAPIEntity = Union[BotAPIMention, BotAPIForward, BotAPIReply]


def _convert_bot_api_mention_to_domain(api_mention_data: BotAPIMentionData) -> Mention:
    entity_id: Optional[UUID] = None
    name: Optional[str] = None

    if api_mention_data.mention_type != BotAPIMentionTypes.ALL:
        mention_data = cast(BotAPINestedMentionData, api_mention_data.mention_data)
        entity_id = mention_data.entity_id
        name = mention_data.name

    return Mention(
        type=convert_mention_type_to_domain(api_mention_data.mention_type),
        entity_id=entity_id,
        name=name,
    )


def convert_bot_api_entity_to_domain(api_entity: BotAPIEntity) -> Entity:
    if api_entity.type == BotAPIEntityTypes.MENTION:
        api_entity = cast(BotAPIMention, api_entity)
        return _convert_bot_api_mention_to_domain(api_entity.data)

    if api_entity.type == BotAPIEntityTypes.FORWARD:
        api_entity = cast(BotAPIForward, api_entity)

        return Forward(
            chat_id=api_entity.data.group_chat_id,
            author_id=api_entity.data.sender_huid,
            sync_id=api_entity.data.source_sync_id,
        )

    if api_entity.type == BotAPIEntityTypes.REPLY:
        api_entity = cast(BotAPIReply, api_entity)

        mentions = MentionList()
        for api_mention_data in api_entity.data.mentions:
            mentions.append(_convert_bot_api_mention_to_domain(api_mention_data))

        return Reply(
            author_id=api_entity.data.sender,
            sync_id=api_entity.data.source_sync_id,
            body=api_entity.data.body,
            mentions=mentions,
        )

    raise NotImplementedError(f"Unsupported entity type: {api_entity.type}")
