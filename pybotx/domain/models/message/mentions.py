import re
from dataclasses import dataclass
from typing import Literal
from uuid import UUID

from pybotx.domain.models.enums import MentionTypes


def build_embed_mention(
    mention_type: MentionTypes,
    entity_id: UUID | None = None,
    name: str | None = None,
) -> str:
    name = name or ""
    entity_id_str = "" if entity_id is None else str(entity_id)
    return f"<embed_mention>{mention_type.value}:{entity_id_str}:{name}</embed_mention>"


@dataclass(slots=True)
class BaseTargetMention:
    entity_id: UUID
    name: str | None


@dataclass(slots=True)
class MentionUser(BaseTargetMention):
    type: Literal[MentionTypes.USER]

    def __str__(self) -> str:
        return build_embed_mention(self.type, self.entity_id, self.name)


@dataclass(slots=True)
class MentionContact(BaseTargetMention):
    type: Literal[MentionTypes.CONTACT]

    def __str__(self) -> str:
        return build_embed_mention(self.type, self.entity_id, self.name)


@dataclass(slots=True)
class MentionChat(BaseTargetMention):
    type: Literal[MentionTypes.CHAT]

    def __str__(self) -> str:
        return build_embed_mention(self.type, self.entity_id, self.name)


@dataclass(slots=True)
class MentionChannel(BaseTargetMention):
    type: Literal[MentionTypes.CHANNEL]

    def __str__(self) -> str:
        return build_embed_mention(self.type, self.entity_id, self.name)


@dataclass(slots=True)
class MentionAll:
    type: Literal[MentionTypes.ALL]

    def __str__(self) -> str:
        return build_embed_mention(self.type)


Mention = (
    MentionUser
    | MentionContact
    | MentionChat
    | MentionChannel
    | MentionAll
)


class MentionBuilder:
    @classmethod
    def user(cls, entity_id: UUID, name: str | None = None) -> MentionUser:
        return MentionUser(
            type=MentionTypes.USER,
            entity_id=entity_id,
            name=name,
        )

    @classmethod
    def contact(
        cls,
        entity_id: UUID,
        name: str | None = None,
    ) -> MentionContact:
        return MentionContact(
            type=MentionTypes.CONTACT,
            entity_id=entity_id,
            name=name,
        )

    @classmethod
    def chat(cls, entity_id: UUID, name: str | None = None) -> MentionChat:
        return MentionChat(
            type=MentionTypes.CHAT,
            entity_id=entity_id,
            name=name,
        )

    @classmethod
    def channel(
        cls,
        entity_id: UUID,
        name: str | None = None,
    ) -> MentionChannel:
        return MentionChannel(
            type=MentionTypes.CHANNEL,
            entity_id=entity_id,
            name=name,
        )

    @classmethod
    def all(cls) -> MentionAll:
        return MentionAll(
            type=MentionTypes.ALL,
        )


class MentionList(list[Mention]):
    @property
    def contacts(self) -> list[MentionContact]:
        return [mention for mention in self if isinstance(mention, MentionContact)]

    @property
    def chats(self) -> list[MentionChat]:
        return [mention for mention in self if isinstance(mention, MentionChat)]

    @property
    def channels(self) -> list[MentionChannel]:
        return [mention for mention in self if isinstance(mention, MentionChannel)]

    @property
    def users(self) -> list[MentionUser]:
        return [mention for mention in self if isinstance(mention, MentionUser)]

    @property
    def all_users_mentioned(self) -> bool:
        for mention in self:
            if mention.type == MentionTypes.ALL:
                return True

        return False
