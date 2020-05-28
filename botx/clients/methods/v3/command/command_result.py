"""Method for sending command result into chat."""

from typing import Optional
from uuid import UUID

from pydantic import Field

from botx.clients.methods.base import AuthorizedBotXMethod
from botx.clients.methods.extractors import extract_generated_sync_id
from botx.clients.types.message_payload import ResultPayload
from botx.clients.types.options import ResultOptions
from botx.clients.types.response_results import PushResult
from botx.models.enums import Recipients
from botx.models.files import File
from botx.models.typing import AvailableRecipients


class CommandResult(AuthorizedBotXMethod[UUID]):
    """Method for sending notification into many chats."""

    __url__ = "/api/v3/botx/command/callback"
    __method__ = "POST"
    __returning__ = PushResult
    __result_extractor__ = extract_generated_sync_id

    sync_id: UUID
    event_sync_id: Optional[UUID] = None
    recipients: AvailableRecipients = Recipients.all
    result: ResultPayload = Field(..., alias="command_result")
    file: Optional[File] = None
    opts: ResultOptions = ResultOptions()
