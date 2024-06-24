from dataclasses import dataclass
from typing import Any, Dict, List, Literal, Optional
from uuid import UUID

from pydantic import Field

from pybotx.models.api_base import VerifiedPayloadBaseModel
from pybotx.models.async_files import APIAsyncFile, File, convert_async_file_to_domain
from pybotx.models.base_command import (
    BotAPIBaseCommand,
    BotAPIChatContext,
    BotAPIDeviceContext,
    BotAPIUserContext,
    BotCommandBase,
)
from pybotx.models.bot_account import BotAccount
from pybotx.models.chats import Chat
from pybotx.models.enums import (
    BotAPICommandTypes,
    BotAPISystemEventTypes,
    convert_chat_type_to_domain,
    convert_client_platform_to_domain,
)
from pybotx.models.message.incoming_message import UserDevice, UserSender


@dataclass
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

    ref: Optional[UUID]
    smartapp_id: UUID
    data: Dict[str, Any]  # noqa: WPS110
    opts: Optional[Dict[str, Any]]
    smartapp_api_version: Optional[int]
    files: List[File]
    chat: Chat
    sender: UserSender


class BotAPISmartAppData(VerifiedPayloadBaseModel):
    ref: UUID
    smartapp_id: UUID
    data: Dict[str, Any]  # noqa: WPS110
    opts: Dict[str, Any]
    smartapp_api_version: int


class BotAPISmartAppPayload(VerifiedPayloadBaseModel):
    body: Literal[BotAPISystemEventTypes.SMARTAPP_EVENT]
    command_type: Literal[BotAPICommandTypes.SYSTEM]
    data: BotAPISmartAppData
    metadata: Dict[str, Any]


class BotAPISmartAppEventContext(
    BotAPIUserContext,
    BotAPIChatContext,
    BotAPIDeviceContext,
):
    """Class for merging contexts."""


class BotAPISmartAppEvent(BotAPIBaseCommand):
    payload: BotAPISmartAppPayload = Field(..., alias="command")
    sender: BotAPISmartAppEventContext = Field(..., alias="from")
    async_files: List[APIAsyncFile]

    def to_domain(self, raw_command: Dict[str, Any]) -> SmartAppEvent:
        device = UserDevice(
            manufacturer=self.sender.manufacturer,
            device_name=self.sender.device,
            os=self.sender.device_software,
            pushes=None,
            timezone=None,
            permissions=None,
            platform=(
                convert_client_platform_to_domain(self.sender.platform)
                if self.sender.platform
                else None
            ),
            platform_package_id=self.sender.platform_package_id,
            app_version=self.sender.app_version,
            locale=self.sender.locale,
        )

        sender = UserSender(
            huid=self.sender.user_huid,
            udid=self.sender.user_udid,
            ad_login=self.sender.ad_login,
            ad_domain=self.sender.ad_domain,
            username=self.sender.username,
            is_chat_admin=self.sender.is_admin,
            is_chat_creator=self.sender.is_creator,
            device=device,
        )

        return SmartAppEvent(
            bot=BotAccount(id=self.bot_id, host=self.sender.host),
            raw_command=raw_command,
            ref=self.payload.data.ref,
            smartapp_id=self.payload.data.smartapp_id,
            data=self.payload.data.data,
            opts=self.payload.data.opts,
            smartapp_api_version=self.payload.data.smartapp_api_version,
            files=[convert_async_file_to_domain(file) for file in self.async_files],
            chat=Chat(
                id=self.sender.group_chat_id,
                type=convert_chat_type_to_domain(self.sender.chat_type),
            ),
            sender=sender,
        )
