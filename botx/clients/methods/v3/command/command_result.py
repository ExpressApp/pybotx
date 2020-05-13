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


class CommandResult(AuthorizedBotXMethod[UUID]):
    __url__ = "/api/v3/botx/command/callback"
    __method__ = "POST"
    __returning__ = PushResult
    __result_extractor__ = extract_generated_sync_id

    sync_id: UUID
    bot_id: UUID
    event_sync_id: Optional[UUID] = None
    recipients: AvailableRecipients = Recipients.all
    result: ResultPayload = Field(..., alias="command_result")
    file: Optional[File] = None
    opts: ResultOptions = ResultOptions()
