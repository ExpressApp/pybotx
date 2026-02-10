from dataclasses import dataclass
from uuid import UUID

from pybotx.domain.models.attachments import IncomingAttachment
from pybotx.domain.models.base_command import BotCommandBase
from pybotx.domain.models.message.incoming_message import Entity


@dataclass(slots=True)
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

    body: str | None
    sync_id: UUID
    chat_id: UUID
    huid: UUID
    attachments: list[IncomingAttachment]
    entities: list[Entity]
