"""Forward entities that can be received in message."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from botx.models.enums import ChatTypes


class Forward(BaseModel):
    """Forward in message."""

    #: ID of chat from which forward received.
    group_chat_id: UUID

    #: ID of user that is author of message.
    sender_huid: UUID

    #: type of forward.
    forward_type: ChatTypes

    #: name of original chat.
    source_chat_name: Optional[str]

    #: id of original message event.
    source_sync_id: Optional[UUID]

    #: id of event creation.
    source_inserted_at: datetime
