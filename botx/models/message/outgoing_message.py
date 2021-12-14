from dataclasses import dataclass
from typing import Any, Dict, List, Union
from uuid import UUID

from botx.missing import Missing, Undefined
from botx.models.attachments import IncomingFileAttachment, OutgoingAttachment
from botx.models.message.markup import BubbleMarkup, KeyboardMarkup


@dataclass
class OutgoingMessage:
    bot_id: UUID
    chat_id: UUID
    body: str
    metadata: Missing[Dict[str, Any]] = Undefined
    bubbles: Missing[BubbleMarkup] = Undefined
    keyboard: Missing[KeyboardMarkup] = Undefined
    file: Missing[Union[IncomingFileAttachment, OutgoingAttachment]] = Undefined
    silent_response: Missing[bool] = Undefined
    markup_auto_adjust: Missing[bool] = Undefined
    recipients: Missing[List[UUID]] = Undefined
    stealth_mode: Missing[bool] = Undefined
    push_notification: Missing[bool] = Undefined
    ignore_mute: Missing[bool] = Undefined