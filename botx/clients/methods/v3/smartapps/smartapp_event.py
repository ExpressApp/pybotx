"""Method for sending smartapp event."""
from typing import Any, Dict, List, Optional
from uuid import UUID

from botx.clients.methods.base import AuthorizedBotXMethod
from botx.models.files import File, MetaFile


class SmartAppEvent(AuthorizedBotXMethod[str]):
    """Method for sending smartapp events."""

    __url__ = "/api/v3/botx/smartapps/event"
    __method__ = "POST"
    __returning__ = str

    #: unique request id
    ref: Optional[UUID] = None

    #: smartapp id
    smartapp_id: UUID

    #: event data
    data: Dict[str, Any]  # noqa: WPS110

    #: event options
    opts: Dict[str, Any] = {}

    #: version of protocol smartapp <-> bot
    smartapp_api_version: int

    #: smartapp chat
    group_chat_id: Optional[UUID]

    #: files
    files: List[File] = []

    #: file's meta to upload
    async_files: List[MetaFile] = []
