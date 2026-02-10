from dataclasses import dataclass
from typing import Any
from uuid import UUID

from pybotx.domain.models.async_files import File
from pybotx.domain.models.base_command import BotCommandBase
from pybotx.domain.models.chats import Chat
from pybotx.domain.models.message.incoming_message import UserSender


@dataclass(slots=True)
class SmartAppEvent(BotCommandBase):
    """Event `system:smartapp_event`.

    Attributes:
        ref: Unique request id.
        smartapp_id: also personnel chat_id.
        data: Payload.
        opts: Request options.
        smartapp_api_version: Protocol version.
        sender: Event sender.
    """

    ref: UUID | None
    smartapp_id: UUID
    data: dict[str, Any]
    opts: dict[str, Any] | None
    smartapp_api_version: int | None
    files: list[File]
    chat: Chat
    sender: UserSender
