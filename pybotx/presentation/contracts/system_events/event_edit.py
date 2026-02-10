from typing import Any, Literal
from uuid import UUID

from pydantic import Field

from pybotx.presentation.contracts.api_base import VerifiedPayloadBaseModel
from pybotx.presentation.contracts.attachments import (
    BotAPIAttachment,
    convert_api_attachment_to_domain,
)
from pybotx.presentation.contracts.base_command import (
    BotAPIBaseCommand,
    BotAPIBaseSystemEventPayload,
    BotAPIUserContext,
)
from pybotx.presentation.contracts.enums import BotAPISystemEventTypes
from pybotx.presentation.contracts.message.incoming_message import (
    BotAPIEntity,
    convert_bot_api_entity_to_domain,
)
from pybotx.domain.models.bot_account import BotAccount
from pybotx.domain.models.system_events.event_edit import EventEdit


class BotAPIEventEditData(VerifiedPayloadBaseModel):
    body: str | None


class BotAPIEventEditPayload(BotAPIBaseSystemEventPayload):
    body: Literal[BotAPISystemEventTypes.EVENT_EDIT]
    data: BotAPIEventEditData


class BotAPIBotContext(BotAPIUserContext):
    """Bot context."""

    group_chat_id: UUID


class BotAPIEventEdit(BotAPIBaseCommand):
    payload: BotAPIEventEditPayload = Field(..., alias="command")
    sender: BotAPIBotContext = Field(..., alias="from")
    attachments: list[BotAPIAttachment]
    entities: list[BotAPIEntity]

    def to_domain(self, raw_command: dict[str, Any]) -> EventEdit:
        return EventEdit(
            bot=BotAccount(
                id=self.bot_id,
                host=self.sender.host,
            ),
            raw_command=raw_command,
            body=self.payload.data.body,
            attachments=[
                convert_api_attachment_to_domain(
                    api_attachment=attachment,
                    message_body=self.payload.body,
                )
                for attachment in self.attachments
            ],
            entities=[
                convert_bot_api_entity_to_domain(api_entity=entity)
                for entity in self.entities
            ],
            sync_id=self.sync_id,
            chat_id=self.sender.group_chat_id,
            huid=self.sender.user_huid,
        )
