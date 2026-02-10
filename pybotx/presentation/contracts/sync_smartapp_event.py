import json
from typing import Any
from uuid import UUID

from pybotx.presentation.contracts.api_base import (
    UnverifiedPayloadBaseModel,
    VerifiedPayloadBaseModel,
)
from pybotx.presentation.contracts.async_files import (
    APIAsyncFile,
    File,
    convert_async_file_from_domain,
    convert_async_file_to_domain,
)
from pybotx.presentation.contracts.enums import (
    BotAPIClientPlatforms,
    convert_client_platform_to_domain,
)
from pybotx.domain.missing import Missing, Undefined
from pybotx.domain.models.bot_account import BotAccount
from pybotx.domain.models.chats import Chat
from pybotx.domain.models.enums import ChatTypes
from pybotx.domain.models.message.incoming_message import UserDevice, UserSender
from pybotx.domain.models.sync_smartapp_event import (
    SyncSmartAppEventError,
    SyncSmartAppEventResponse,
    SyncSmartAppEventResult,
)
from pybotx.domain.models.system_events.smartapp_event import SmartAppEvent


class BotAPISyncSmartAppSender(VerifiedPayloadBaseModel):
    user_huid: UUID
    udid: UUID | None
    platform: BotAPIClientPlatforms | None


class BotAPISyncSmartAppPayload(VerifiedPayloadBaseModel):
    data: dict[str, Any]
    files: list[APIAsyncFile]


class BotAPISyncSmartAppEvent(VerifiedPayloadBaseModel):
    bot_id: UUID
    group_chat_id: UUID
    sender_info: BotAPISyncSmartAppSender
    method: str
    payload: BotAPISyncSmartAppPayload

    def to_domain(self, raw_smartapp_event: dict[str, Any]) -> SmartAppEvent:
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
    files: list[APIAsyncFile]

    @classmethod
    def from_domain(
        cls,
        data: Any,
        files: Missing[list[File]] = Undefined,
    ) -> "BotAPISyncSmartAppEventResultResponse":
        api_async_files: list[APIAsyncFile] = []
        if files:
            api_async_files = [convert_async_file_from_domain(file) for file in files]

        return cls(
            data=data,
            files=api_async_files,
        )

    def jsonable_dict(self) -> dict[str, Any]:
        return {
            "status": "ok",
            "result": json.loads(self.json()),
        }


class BotAPISyncSmartAppEventErrorResponse(UnverifiedPayloadBaseModel):
    reason: str
    errors: list[Any]
    error_data: dict[str, Any]

    @classmethod
    def from_domain(
        cls,
        reason: Missing[str] = Undefined,
        errors: Missing[list[Any]] = Undefined,
        error_data: Missing[dict[str, Any]] = Undefined,
    ) -> "BotAPISyncSmartAppEventErrorResponse":
        return cls(
            reason="smartapp_error" if reason is Undefined else reason,
            errors=[] if errors is Undefined else errors,
            error_data={} if error_data is Undefined else error_data,
        )

    def jsonable_dict(self) -> dict[str, Any]:
        return {
            "status": "error",
            **json.loads(self.json()),
        }


BotAPISyncSmartAppEventResponse = (
    BotAPISyncSmartAppEventResultResponse
    | BotAPISyncSmartAppEventErrorResponse
)


def convert_sync_smartapp_event_response(
    response: SyncSmartAppEventResponse | BotAPISyncSmartAppEventResponse,
) -> BotAPISyncSmartAppEventResponse:
    if isinstance(
        response,
        (BotAPISyncSmartAppEventResultResponse, BotAPISyncSmartAppEventErrorResponse),
    ):
        return response

    if isinstance(response, SyncSmartAppEventResult):
        return BotAPISyncSmartAppEventResultResponse.from_domain(
            data=response.data,
            files=response.files,
        )

    if isinstance(response, SyncSmartAppEventError):
        return BotAPISyncSmartAppEventErrorResponse.from_domain(
            reason=response.reason,
            errors=response.errors,
            error_data=response.error_data,
        )

    raise TypeError(
        "Unsupported sync smartapp event response type",
    )


__all__ = (
    "BotAPISyncSmartAppSender",
    "BotAPISyncSmartAppPayload",
    "BotAPISyncSmartAppEvent",
    "BotAPISyncSmartAppEventResultResponse",
    "BotAPISyncSmartAppEventErrorResponse",
    "BotAPISyncSmartAppEventResponse",
    "convert_sync_smartapp_event_response",
)
