from typing import Optional
from uuid import UUID

from pydantic import Field

from botx.clients.methods.base import AuthorizedBotXMethod
from botx.clients.methods.extractors import extract_generated_sync_id
from botx.clients.types.options import ResultOptions
from botx.clients.types.push_response import PushResult
from botx.clients.types.result_payload import ResultPayload
from botx.models.enums import Recipients
from botx.models.files import File
from botx.models.typing import AvailableRecipients


class NotificationDirect(AuthorizedBotXMethod[UUID]):
    __url__ = "/api/v3/botx/notification/callback/direct"
    __method__ = "POST"
    __returning__ = PushResult
    __result_extractor__ = extract_generated_sync_id

    bot_id: UUID
    group_chat_id: UUID
    event_sync_id: Optional[UUID] = None
    recipients: AvailableRecipients = Recipients.all
    result: ResultPayload = Field(..., alias="notification")
    file: Optional[File] = None
    opts: ResultOptions = ResultOptions()
