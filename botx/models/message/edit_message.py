from dataclasses import dataclass
from typing import Any, Dict, Union
from uuid import UUID

from botx.missing import Missing, Undefined
from botx.models.attachments import IncomingFileAttachment, OutgoingAttachment
from botx.models.message.markup import BubbleMarkup, KeyboardMarkup


@dataclass
class EditMessage:
    bot_id: UUID
    sync_id: UUID
    body: Missing[str] = Undefined
    metadata: Missing[Dict[str, Any]] = Undefined
    bubbles: Missing[BubbleMarkup] = Undefined
    keyboard: Missing[KeyboardMarkup] = Undefined
    file: Missing[Union[IncomingFileAttachment, OutgoingAttachment]] = Undefined
    markup_auto_adjust: Missing[bool] = Undefined
