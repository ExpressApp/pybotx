from typing import List, Optional, Union
from uuid import UUID

from pydantic import Field

from botx.clients.methods.base import AuthorizedBotXMethod
from botx.models.enums import Recipients
from botx.models.files import File
from botx.models.requests import ResultOptions, ResultPayload


class Notification(AuthorizedBotXMethod[str]):
    __url__ = "/api/v3/botx/notification/callback"
    __method__ = "POST"
    __returning__ = str

    recipients: Union[List[UUID], Recipients] = Recipients.all
    group_chat_ids: List[UUID] = []
    result: ResultPayload = Field(..., alias="notification")
    file: Optional[File] = None
    opts: ResultOptions = ResultOptions()
