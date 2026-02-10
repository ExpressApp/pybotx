from dataclasses import dataclass
from typing import Any
from uuid import UUID

from pybotx.domain.missing import Missing, Undefined
from pybotx.domain.models.attachments import IncomingFileAttachment, OutgoingAttachment
from pybotx.domain.models.message.markup import BubbleMarkup, KeyboardMarkup


@dataclass(slots=True)
class EditMessage:
    bot_id: UUID
    sync_id: UUID
    body: Missing[str] = Undefined
    metadata: Missing[dict[str, Any]] = Undefined
    bubbles: Missing[BubbleMarkup] = Undefined
    keyboard: Missing[KeyboardMarkup] = Undefined
    file: Missing[IncomingFileAttachment | OutgoingAttachment] = Undefined
    markup_auto_adjust: Missing[bool] = Undefined
