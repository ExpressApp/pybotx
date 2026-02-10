from __future__ import annotations

from uuid import UUID

from pybotx.domain.models.enums import MentionTypes
from pybotx.domain.models.message.mentions import Mention, MentionBuilder, build_embed_mention


class TextBuilder:
    def __init__(self, parts: list[str] | None = None) -> None:
        self._parts: list[str] = list(parts or [])

    def append(self, text: str) -> "TextBuilder":
        self._parts.append(text)
        return self

    def space(self) -> "TextBuilder":
        self._parts.append(" ")
        return self

    def newline(self) -> "TextBuilder":
        self._parts.append("\n")
        return self

    def mention(self, mention: Mention) -> "TextBuilder":
        self._parts.append(str(mention))
        return self

    def mention_user(self, entity_id: UUID, name: str | None = None) -> "TextBuilder":
        return self.mention(MentionBuilder.user(entity_id, name))

    def mention_user_named(self, name: str, entity_id: UUID) -> "TextBuilder":
        return self.mention_user(entity_id, name)

    def mention_contact(
        self,
        entity_id: UUID,
        name: str | None = None,
    ) -> "TextBuilder":
        return self.mention(MentionBuilder.contact(entity_id, name))

    def mention_contact_named(self, name: str, entity_id: UUID) -> "TextBuilder":
        return self.mention_contact(entity_id, name)

    def mention_chat(self, entity_id: UUID, name: str | None = None) -> "TextBuilder":
        return self.mention(MentionBuilder.chat(entity_id, name))

    def mention_chat_named(self, name: str, entity_id: UUID) -> "TextBuilder":
        return self.mention_chat(entity_id, name)

    def mention_channel(
        self,
        entity_id: UUID,
        name: str | None = None,
    ) -> "TextBuilder":
        return self.mention(MentionBuilder.channel(entity_id, name))

    def mention_channel_named(self, name: str, entity_id: UUID) -> "TextBuilder":
        return self.mention_channel(entity_id, name)

    def mention_all(self) -> "TextBuilder":
        return self.mention(MentionBuilder.all())

    def join(
        self,
        parts: list[str],
        *,
        separator: str = "",
        prefix: str = "",
        suffix: str = "",
    ) -> "TextBuilder":
        if not parts:
            return self
        if prefix:
            self._parts.append(prefix)
        self._parts.append(separator.join(parts))
        if suffix:
            self._parts.append(suffix)
        return self

    def embed(
        self,
        *,
        mention_type: MentionTypes,
        entity_id: UUID | None = None,
        name: str | None = None,
    ) -> "TextBuilder":
        self._parts.append(
            build_embed_mention(
                mention_type=mention_type,
                entity_id=entity_id,
                name=name,
            ),
        )
        return self

    def build(self) -> str:
        return "".join(self._parts)

    def __str__(self) -> str:
        return self.build()


class MentionComposer(TextBuilder):
    pass


__all__ = ("TextBuilder", "MentionComposer")
