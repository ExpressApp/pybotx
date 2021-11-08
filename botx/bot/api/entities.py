from datetime import datetime
from typing import Union, cast
from uuid import UUID

from botx.bot.api.enums import (
    BotAPIEntityTypes,
    BotAPIMentionTypes,
    convert_mention_type_to_domain,
)
from botx.bot.models.commands.entities import Entity, Forward, Mention, Reply
from botx.shared_models.api_base import VerifiedPayloadBaseModel
from botx.shared_models.chat_types import APIChatTypes, convert_chat_type_to_domain

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal  # type: ignore  # noqa: WPS440


class BotAPINestedMentionData(VerifiedPayloadBaseModel):
    user_huid: UUID
    name: str
    conn_type: str


class BotAPIMentionData(VerifiedPayloadBaseModel):
    mention_type: BotAPIMentionTypes
    mention_id: UUID
    mention_data: BotAPINestedMentionData


class BotAPIMention(VerifiedPayloadBaseModel):
    type: Literal[BotAPIEntityTypes.MENTION]
    data: BotAPIMentionData


class BotAPIForwardData(VerifiedPayloadBaseModel):
    group_chat_id: UUID
    sender_huid: UUID
    forward_type: APIChatTypes
    source_chat_name: str
    source_sync_id: UUID
    source_inserted_at: datetime


class BotAPIForward(VerifiedPayloadBaseModel):
    type: Literal[BotAPIEntityTypes.FORWARD]
    data: BotAPIForwardData


class BotAPIReplyData(VerifiedPayloadBaseModel):
    source_sync_id: UUID
    sender: UUID
    body: str
    # TODO: Mentions
    # TODO: Attachment
    reply_type: APIChatTypes
    source_group_chat_id: UUID
    source_chat_name: str


class BotAPIReply(VerifiedPayloadBaseModel):
    type: Literal[BotAPIEntityTypes.REPLY]
    data: BotAPIReplyData


BotAPIEntity = Union[BotAPIMention, BotAPIForward, BotAPIReply]


def convert_bot_api_entity_to_domain(api_entity: BotAPIEntity) -> Entity:
    if api_entity.type == BotAPIEntityTypes.MENTION:
        api_entity = cast(BotAPIMention, api_entity)

        return Mention(
            type=convert_mention_type_to_domain(api_entity.data.mention_type),
            huid=api_entity.data.mention_data.user_huid,
            name=api_entity.data.mention_data.name,
        )

    if api_entity.type == BotAPIEntityTypes.FORWARD:
        api_entity = cast(BotAPIForward, api_entity)

        return Forward(
            chat_id=api_entity.data.group_chat_id,
            huid=api_entity.data.sender_huid,
            type=convert_chat_type_to_domain(api_entity.data.forward_type),
            chat_name=api_entity.data.source_chat_name,
            sync_id=api_entity.data.source_sync_id,
            created_at=api_entity.data.source_inserted_at,
        )

    if api_entity.type == BotAPIEntityTypes.REPLY:
        api_entity = cast(BotAPIReply, api_entity)

        return Reply(
            chat_id=api_entity.data.source_group_chat_id,
            huid=api_entity.data.sender,
            type=convert_chat_type_to_domain(api_entity.data.reply_type),
            chat_name=api_entity.data.source_chat_name,
            sync_id=api_entity.data.source_sync_id,
            body=api_entity.data.body,
        )

    raise NotImplementedError(f"Unsupported entity type: {api_entity.type}")
