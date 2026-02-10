from typing import Literal
from uuid import UUID

from pydantic import Field, field_validator

from pybotx.presentation.contracts.api_base import (
    VerifiedPayloadBaseModel,
)
from pybotx.presentation.contracts.enums import (
    BotAPIEntityTypes,
    BotAPIMentionTypes,
)


class BotAPINestedPersonalMentionData(VerifiedPayloadBaseModel):
    entity_id: UUID = Field(alias="user_huid")
    name: str
    conn_type: str


class BotAPINestedGroupMentionData(VerifiedPayloadBaseModel):
    entity_id: UUID = Field(alias="group_chat_id")
    name: str


BotAPINestedMentionData = (
    BotAPINestedPersonalMentionData
    | BotAPINestedGroupMentionData
)


class BotAPIMentionData(VerifiedPayloadBaseModel):
    mention_type: BotAPIMentionTypes
    mention_id: UUID
    mention_data: BotAPINestedMentionData | None

    @field_validator("mention_data", mode="before")
    @classmethod
    def validate_mention_data(
        cls,
        mention_data: dict[str, str],
    ) -> dict[str, str] | None:
        # Mention data can be an empty dict
        if not mention_data:
            return None

        return mention_data


class BotAPIMention(VerifiedPayloadBaseModel):
    type: Literal[BotAPIEntityTypes.MENTION]
    data: BotAPIMentionData
