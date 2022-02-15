import re
from dataclasses import dataclass
from typing import Dict, List, Literal, Optional, Tuple, Union
from uuid import UUID, uuid4

from pydantic import Field, validator

from botx.missing import Missing, Undefined
from botx.models.api_base import UnverifiedPayloadBaseModel, VerifiedPayloadBaseModel
from botx.models.enums import (
    BotAPIEntityTypes,
    BotAPIMentionTypes,
    MentionTypes,
    convert_mention_type_from_domain,
)


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


class BotXAPIPersonalMentionData(UnverifiedPayloadBaseModel):
    user_huid: UUID
    name: Missing[str]


class BotXAPIUserMention(UnverifiedPayloadBaseModel):
    mention_type: Literal[BotAPIMentionTypes.USER]
    mention_id: UUID
    mention_data: BotXAPIPersonalMentionData

    def to_botx_embed_mention_format(self) -> str:
        return f"@{{mention:{self.mention_id}}}"


class BotXAPIContactMention(UnverifiedPayloadBaseModel):
    mention_type: Literal[BotAPIMentionTypes.CONTACT]
    mention_id: UUID
    mention_data: BotXAPIPersonalMentionData

    def to_botx_embed_mention_format(self) -> str:
        return f"@@{{mention:{self.mention_id}}}"


class BotXAPIGroupMentionData(UnverifiedPayloadBaseModel):
    group_chat_id: UUID
    name: Missing[str]


class BotXAPIChatMention(UnverifiedPayloadBaseModel):
    mention_type: Literal[BotAPIMentionTypes.CHAT]
    mention_id: UUID
    mention_data: BotXAPIGroupMentionData

    def to_botx_embed_mention_format(self) -> str:
        return f"##{{mention:{self.mention_id}}}"


class BotXAPIChannelMention(UnverifiedPayloadBaseModel):
    mention_type: Literal[BotAPIMentionTypes.CHANNEL]
    mention_id: UUID
    mention_data: BotXAPIGroupMentionData

    def to_botx_embed_mention_format(self) -> str:
        return f"##{{mention:{self.mention_id}}}"


class BotXAPIAllMention(UnverifiedPayloadBaseModel):
    mention_type: Literal[BotAPIMentionTypes.ALL]
    mention_id: UUID

    def to_botx_embed_mention_format(self) -> str:
        return f"@{{mention:{self.mention_id}}}"


BotXAPIMention = Union[
    BotXAPIUserMention,
    BotXAPIContactMention,
    BotXAPIChatMention,
    BotXAPIChannelMention,
    BotXAPIAllMention,
]


def build_botx_api_embed_mention(
    mention_dict: Dict[str, str],
) -> BotXAPIMention:
    mention_type = MentionTypes(mention_dict["mention_type"])
    mentioned_entity_id = mention_dict["mentioned_entity_id"]
    # re match will have "" if mention_name not passed
    mention_name = mention_dict["mention_name"] or Undefined

    if mention_type == MentionTypes.USER:
        return BotXAPIUserMention(
            mention_type=convert_mention_type_from_domain(mention_type),
            mention_id=uuid4(),
            mention_data=BotXAPIPersonalMentionData(
                user_huid=UUID(mentioned_entity_id),
                name=mention_name,
            ),
        )

    if mention_type == MentionTypes.CONTACT:
        return BotXAPIContactMention(
            mention_type=convert_mention_type_from_domain(mention_type),
            mention_id=uuid4(),
            mention_data=BotXAPIPersonalMentionData(
                user_huid=UUID(mentioned_entity_id),
                name=mention_name,
            ),
        )

    if mention_type == MentionTypes.CHAT:
        return BotXAPIChatMention(
            mention_type=convert_mention_type_from_domain(mention_type),
            mention_id=uuid4(),
            mention_data=BotXAPIGroupMentionData(
                group_chat_id=UUID(mentioned_entity_id),
                name=mention_name,
            ),
        )

    if mention_type == MentionTypes.CHANNEL:
        return BotXAPIChannelMention(
            mention_type=convert_mention_type_from_domain(mention_type),
            mention_id=uuid4(),
            mention_data=BotXAPIGroupMentionData(
                group_chat_id=UUID(mentioned_entity_id),
                name=mention_name,
            ),
        )

    if mention_type == MentionTypes.ALL:
        return BotXAPIAllMention(
            mention_type=convert_mention_type_from_domain(mention_type),
            mention_id=uuid4(),
        )

    raise NotImplementedError


EMBED_MENTION_RE = re.compile(
    (
        "<embed_mention>"
        "(?P<mention_type>.+?):"
        r"(?P<mentioned_entity_id>[0-9a-f\-]*?):"
        "(?P<mention_name>.*?)"
        r"<\/embed_mention>"
    ),
)


def find_and_replace_embed_mentions(body: str) -> Tuple[str, List[BotXAPIMention]]:
    mentions = []

    for match in EMBED_MENTION_RE.finditer(body):
        mention_dict = match.groupdict()
        embed_mention = match.group(0)

        mention = build_botx_api_embed_mention(mention_dict)
        body = body.replace(embed_mention, mention.to_botx_embed_mention_format(), 1)

        mentions.append(mention)

    return body, mentions
