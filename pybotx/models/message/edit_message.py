from dataclasses import dataclass
from typing import Any, Dict, Union
from uuid import UUID

from pybotx.missing import Missing, Undefined
from pybotx.models.attachments import IncomingFileAttachment, OutgoingAttachment
from pybotx.models.message.markup import BubbleMarkup, KeyboardMarkup


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
