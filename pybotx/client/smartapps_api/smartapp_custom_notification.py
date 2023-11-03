from typing import Any, Dict, Literal, Optional
from uuid import UUID

from pybotx.client.authorized_botx_method import AuthorizedBotXMethod
from pybotx.missing import Missing
from pybotx.models.api_base import UnverifiedPayloadBaseModel, VerifiedPayloadBaseModel


class BotXAPISmartAppCustomNotificationNestedPayload(UnverifiedPayloadBaseModel):
    title: str
    body: str


class BotXAPISmartAppCustomNotificationRequestPayload(UnverifiedPayloadBaseModel):
    group_chat_id: UUID
    payload: BotXAPISmartAppCustomNotificationNestedPayload
    meta: Missing[Dict[str, Any]]

    @classmethod
    def from_domain(
        cls,
        group_chat_id: UUID,
        title: str,
        body: str,
        meta: Missing[Dict[str, Any]],
    ) -> "BotXAPISmartAppCustomNotificationRequestPayload":
        return cls(
            group_chat_id=group_chat_id,
            payload=BotXAPISmartAppCustomNotificationNestedPayload(
                title=title,
                body=body,
            ),
            meta=meta,
        )


class BotXAPISyncIdResult(VerifiedPayloadBaseModel):
    sync_id: UUID


class BotXAPISmartAppCustomNotificationResponsePayload(VerifiedPayloadBaseModel):
    status: Literal["ok"]
    result: BotXAPISyncIdResult

    def to_domain(self) -> UUID:
        return self.result.sync_id


class SmartAppCustomNotificationMethod(AuthorizedBotXMethod):
    error_callback_handlers = {
        **AuthorizedBotXMethod.error_callback_handlers,
    }

    async def execute(
        self,
        payload: BotXAPISmartAppCustomNotificationRequestPayload,
        wait_callback: bool,
        callback_timeout: Optional[float],
        default_callback_timeout: float,
    ) -> BotXAPISmartAppCustomNotificationResponsePayload:
        path = "/api/v4/botx/smartapps/notification"

        response = await self._botx_method_call(
            "POST",
            self._build_url(path),
            json=payload.jsonable_dict(),
        )

        api_model = self._verify_and_extract_api_model(
            BotXAPISmartAppCustomNotificationResponsePayload,
            response,
        )

        await self._process_callback(
            api_model.result.sync_id,
            wait_callback,
            callback_timeout,
            default_callback_timeout,
        )

        return api_model
