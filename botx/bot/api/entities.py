from datetime import datetime
from typing import Dict, Optional, Union, cast
from uuid import UUID

from pydantic import Field, validator

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

        entity_id: Optional[UUID] = None
        name: Optional[str] = None
        if api_entity.data.mention_type != BotAPIMentionTypes.ALL:
            mention_data = cast(BotAPINestedMentionData, api_entity.data.mention_data)
            entity_id = mention_data.entity_id
            name = mention_data.name

        return Mention(
            type=convert_mention_type_to_domain(api_entity.data.mention_type),
            entity_id=entity_id,
            name=name,
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
