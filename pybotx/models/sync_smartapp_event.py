import json
from typing import Any, Dict, List, Optional, Union
from uuid import UUID

from pybotx.missing import Missing, Undefined
from pybotx.models.api_base import UnverifiedPayloadBaseModel, VerifiedPayloadBaseModel
from pybotx.models.async_files import (
    APIAsyncFile,
    File,
    convert_async_file_from_domain,
    convert_async_file_to_domain,
)
from pybotx.models.bot_account import BotAccount
from pybotx.models.chats import Chat
from pybotx.models.enums import (
    BotAPIClientPlatforms,
    ChatTypes,
    convert_client_platform_to_domain,
)
from pybotx.models.message.incoming_message import UserDevice, UserSender
from pybotx.models.system_events.smartapp_event import SmartAppEvent


class BotAPISyncSmartAppSender(VerifiedPayloadBaseModel):
    user_huid: UUID
    udid: Optional[UUID]
    platform: Optional[BotAPIClientPlatforms]


class BotAPISyncSmartAppPayload(VerifiedPayloadBaseModel):
    data: Dict[str, Any]
    files: List[APIAsyncFile]


class BotAPISyncSmartAppEvent(VerifiedPayloadBaseModel):
    bot_id: UUID
    group_chat_id: UUID
    sender_info: BotAPISyncSmartAppSender
    method: str
    payload: BotAPISyncSmartAppPayload

    def to_domain(self, raw_smartapp_event: Dict[str, Any]) -> SmartAppEvent:
        platform = (
            convert_client_platform_to_domain(self.sender_info.platform)
            if self.sender_info.platform
            else None
        )

        device = UserDevice(
            platform=platform,
            manufacturer=None,
            device_name=None,
            os=None,
            pushes=None,
            timezone=None,
            permissions=None,
            platform_package_id=None,
            app_version=None,
            locale=None,
        )

        sender = UserSender(
            huid=self.sender_info.user_huid,
            udid=self.sender_info.udid,
            device=device,
            ad_login=None,
            ad_domain=None,
            username=None,
            is_chat_admin=None,
            is_chat_creator=None,
        )

        return SmartAppEvent(
            bot=BotAccount(id=self.bot_id, host=None),
            chat=Chat(
                id=self.group_chat_id,
                type=ChatTypes.PERSONAL_CHAT,
            ),
            sender=sender,
            data={
                "method": self.method,
                "type": "smartapp_rpc",
                "params": self.payload.data,
            },
            ref=None,
            smartapp_id=self.bot_id,
            opts=None,
            files=[convert_async_file_to_domain(file) for file in self.payload.files],
            smartapp_api_version=None,
            raw_command=raw_smartapp_event,
        )


class BotAPISyncSmartAppEventResultResponse(UnverifiedPayloadBaseModel):
    data: Any
    files: List[APIAsyncFile]

    @classmethod
    def from_domain(
        cls,
        data: Any,
        files: Missing[List[File]] = Undefined,
    ) -> "BotAPISyncSmartAppEventResultResponse":
        api_async_files: List[APIAsyncFile] = []
        if files:
            api_async_files = [convert_async_file_from_domain(file) for file in files]

        return cls(
            data=data,
            files=api_async_files,
        )

    def jsonable_dict(self) -> Dict[str, Any]:
        return {
            "status": "ok",
            "result": json.loads(self.json()),
        }


class BotAPISyncSmartAppEventErrorResponse(UnverifiedPayloadBaseModel):
    reason: str
    errors: List[Any]
    error_data: Dict[str, Any]

    @classmethod
    def from_domain(
        cls,
        reason: Missing[str] = Undefined,
        errors: Missing[List[Any]] = Undefined,
        error_data: Missing[Dict[str, Any]] = Undefined,
    ) -> "BotAPISyncSmartAppEventErrorResponse":
        return cls(
            reason="smartapp_error" if reason is Undefined else reason,
            errors=[] if errors is Undefined else errors,
            error_data={} if error_data is Undefined else error_data,
        )

    def jsonable_dict(self) -> Dict[str, Any]:
        return {
            "status": "error",
            **json.loads(self.json()),
        }


BotAPISyncSmartAppEventResponse = Union[
    BotAPISyncSmartAppEventResultResponse,
    BotAPISyncSmartAppEventErrorResponse,
]
