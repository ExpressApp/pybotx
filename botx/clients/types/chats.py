from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel

from botx import ChatTypes
from botx.models.events import UserInChatCreated


class ChatFromSearch(BaseModel):
    name: str
    description: Optional[UUID]
    chat_type: ChatTypes
    creator: UUID
    group_chat_id: UUID
    members: List[UserInChatCreated]
