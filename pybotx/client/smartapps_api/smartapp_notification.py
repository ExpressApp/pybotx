from typing import Any, Dict, Literal
from uuid import UUID

from pybotx.client.authorized_botx_method import AuthorizedBotXMethod
from pybotx.constants import SMARTAPP_API_VERSION
from pybotx.missing import Missing
from pybotx.models.api_base import UnverifiedPayloadBaseModel, VerifiedPayloadBaseModel


class BotXAPISmartAppNotificationRequestPayload(UnverifiedPayloadBaseModel):
    group_chat_id: UUID
    smartapp_counter: int
    body: Missing[str]
    opts: Missing[Dict[str, Any]]
    meta: Missing[Dict[str, Any]]
    smartapp_api_version: int

    @classmethod
    def from_domain(
        cls,
        chat_id: UUID,
        smartapp_counter: int,
        body: Missing[str],
        opts: Missing[Dict[str, Any]],
        meta: Missing[Dict[str, Any]],
    ) -> "BotXAPISmartAppNotificationRequestPayload":
        return cls(
            group_chat_id=chat_id,
            smartapp_counter=smartapp_counter,
            body=body,
            opts=opts,
            meta=meta,
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
