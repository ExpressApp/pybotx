from typing import List, Optional
from uuid import UUID

from httpx import StatusCode

from botx.clients.methods.base import AuthorizedBotXMethod
from botx.clients.methods.errors import chat_creation_disallowed, chat_creation_error
from botx.clients.methods.extractors import extract_generated_chat_id
from botx.clients.types.response_results import ChatCreatedResult
from botx.models.enums import ChatTypes


class Create(AuthorizedBotXMethod[UUID]):
    __url__ = "/api/v3/botx/chats/create"
    __method__ = "POST"
    __returning__ = ChatCreatedResult
    __result_extractor__ = extract_generated_chat_id
    __errors_handlers__ = {
        StatusCode.FORBIDDEN: chat_creation_disallowed.handle_error,
        StatusCode.UNPROCESSABLE_ENTITY: chat_creation_error.handle_error,
    }

    name: str
    description: Optional[str] = None
    members: List[UUID]
    avatar: Optional[str] = None
    chat_type: ChatTypes
