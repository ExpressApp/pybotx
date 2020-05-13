from typing import List, Optional
from uuid import UUID

from pydantic import Field

from botx.clients.methods.base import AuthorizedBotXMethod
from botx.clients.types.options import ResultOptions
from botx.clients.types.result_payload import ResultPayload
from botx.models.enums import Recipients
from botx.models.files import File
from botx.models.typing import AvailableRecipients


class Notification(AuthorizedBotXMethod[str]):
    __url__ = "/api/v3/botx/notification/callback"
    __method__ = "POST"
    __returning__ = str

    bot_id: UUID
    group_chat_ids: List[UUID] = []
    recipients: AvailableRecipients = Recipients.all
    result: ResultPayload = Field(..., alias="notification")
    file: Optional[File] = None
    opts: ResultOptions = ResultOptions()
