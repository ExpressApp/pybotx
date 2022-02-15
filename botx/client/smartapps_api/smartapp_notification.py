from typing import Any, Dict, Literal
from uuid import UUID

from botx.client.authorized_botx_method import AuthorizedBotXMethod
from botx.constants import SMARTAPP_API_VERSION
from botx.missing import Missing
from botx.models.api_base import UnverifiedPayloadBaseModel, VerifiedPayloadBaseModel


class BotXAPISmartAppNotificationRequestPayload(UnverifiedPayloadBaseModel):
    group_chat_id: UUID
    smartapp_counter: int
    opts: Missing[Dict[str, Any]]
    smartapp_api_version: int

    @classmethod
    def from_domain(
        cls,
        chat_id: UUID,
        smartapp_counter: int,
        opts: Missing[Dict[str, Any]],
    ) -> "BotXAPISmartAppNotificationRequestPayload":
        return cls(
            group_chat_id=chat_id,
            smartapp_counter=smartapp_counter,
            opts=opts,
            smartapp_api_version=SMARTAPP_API_VERSION,
        )


class BotXAPISmartAppNotificationResponsePayload(VerifiedPayloadBaseModel):
    status: Literal["ok"]


class SmartAppNotificationMethod(AuthorizedBotXMethod):
    async def execute(
        self,
        payload: BotXAPISmartAppNotificationRequestPayload,
    ) -> None:
        path = "/api/v3/botx/smartapps/notification"

        # TODO: Remove opts
        # UnverifiedPayloadBaseModel.jsonable_dict remove empty dicts
        json = payload.jsonable_dict()
        json["opts"] = json.get("opts", {})

        response = await self._botx_method_call(
            "POST",
            self._build_url(path),
            json=json,
        )

        self._verify_and_extract_api_model(
            BotXAPISmartAppNotificationResponsePayload,
            response,
        )
