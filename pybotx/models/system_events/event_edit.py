from dataclasses import dataclass
from typing import Any, Dict, List, Literal, Optional
from uuid import UUID

from pydantic import Field

from pybotx.models.api_base import VerifiedPayloadBaseModel
from pybotx.models.attachments import (
    BotAPIAttachment,
    IncomingAttachment,
    convert_api_attachment_to_domain,
)
from pybotx.models.base_command import (
    BotAPIBaseCommand,
    BotAPIBaseSystemEventPayload,
    BotAPIUserContext,
    BotCommandBase,
)
from pybotx.models.bot_account import BotAccount
from pybotx.models.enums import BotAPISystemEventTypes
from pybotx.models.message.incoming_message import (
    BotAPIEntity,
    Entity,
    convert_bot_api_entity_to_domain,
)


@dataclass
class EventEdit(BotCommandBase):
    """Event `system:event_edit`.

    Attributes:
        body: Updated message body.
        sync_id: Updated message sync id.
        chat_id: Updated message chat id.
        huid: Updated message user huid.
        attachments: Attachments from updated message.
        entities: Entities from updated message.
    """

    body: Optional[str]
    sync_id: UUID
    chat_id: UUID
    huid: UUID
    attachments: List[IncomingAttachment]
    entities: List[Entity]


class BotAPIEventEditData(VerifiedPayloadBaseModel):
    body: Optional[str]


class BotAPIEventEditPayload(BotAPIBaseSystemEventPayload):
    body: Literal[BotAPISystemEventTypes.EVENT_EDIT]
    data: BotAPIEventEditData


class BotAPIBotContext(BotAPIUserContext):
    """Bot context."""

    group_chat_id: UUID


class BotAPIEventEdit(BotAPIBaseCommand):
    payload: BotAPIEventEditPayload = Field(..., alias="command")
    sender: BotAPIBotContext = Field(..., alias="from")
    attachments: List[BotAPIAttachment]
    entities: List[BotAPIEntity]

    def to_domain(self, raw_command: Dict[str, Any]) -> EventEdit:
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
