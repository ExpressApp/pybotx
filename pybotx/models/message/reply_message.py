from dataclasses import dataclass
from typing import Any, Dict, Union
from uuid import UUID

from pybotx.missing import Missing, Undefined
from pybotx.models.attachments import IncomingFileAttachment, OutgoingAttachment
from pybotx.models.message.markup import BubbleMarkup, KeyboardMarkup


@dataclass
class ReplyMessage:
    bot_id: UUID
    sync_id: UUID
    body: str
    metadata: Missing[Dict[str, Any]] = Undefined
    bubbles: Missing[BubbleMarkup] = Undefined
    keyboard: Missing[KeyboardMarkup] = Undefined
    file: Missing[Union[IncomingFileAttachment, OutgoingAttachment]] = Undefined
    silent_response: Missing[bool] = Undefined
    markup_auto_adjust: Missing[bool] = Undefined
    stealth_mode: Missing[bool] = Undefined
    send_push: Missing[bool] = Undefined
    ignore_mute: Missing[bool] = Undefined
