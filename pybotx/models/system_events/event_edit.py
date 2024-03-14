from dataclasses import dataclass
from typing import Any, Dict, List, Literal, Optional

from pydantic import Field

from pybotx.models.api_base import VerifiedPayloadBaseModel
from pybotx.models.attachments import (
    BotAPIAttachment,
    IncomingAttachment,
    convert_api_attachment_to_domain,
)
from pybotx.models.base_command import (
    BaseBotAPIContext,
    BotAPIBaseCommand,
    BotAPIBaseSystemEventPayload,
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
        attachments: Attachments from updated message.
        entities: Entities from updated message.
    """

    body: Optional[str]
    attachments: List[IncomingAttachment]
    entities: List[Entity]


class BotAPIEventEditData(VerifiedPayloadBaseModel):
    body: Optional[str]


class BotAPIEventEditPayload(BotAPIBaseSystemEventPayload):
    body: Literal[BotAPISystemEventTypes.EVENT_EDIT]
    data: BotAPIEventEditData


class BotAPIEventEdit(BotAPIBaseCommand):
    payload: BotAPIEventEditPayload = Field(..., alias="command")
    sender: BaseBotAPIContext = Field(..., alias="from")
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
        )
