from typing import List, Optional, Union
from uuid import UUID

from pydantic import Field

from botx.clients.methods.base import AuthorizedBotXMethod
from botx.clients.methods.extractors import extract_generated_sync_id
from botx.models.enums import Recipients
from botx.models.files import File
from botx.models.requests import ResultOptions, ResultPayload
from botx.models.responses import PushResult


class NotificationDirect(AuthorizedBotXMethod[UUID]):
    __url__ = "/api/v3/botx/notification/callback/direct"
    __method__ = "POST"
    __returning__ = PushResult
    __result_extractor__ = extract_generated_sync_id

    group_chat_id: UUID
    event_sync_id: Optional[UUID] = None
    recipients: Union[List[UUID], Recipients] = Recipients.all
    result: ResultPayload = Field(..., alias="notification")
    file: Optional[File] = None
    opts: ResultOptions = ResultOptions()
