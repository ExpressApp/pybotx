from typing import Any, Dict, List, Literal
from uuid import UUID

from pybotx.client.authorized_botx_method import AuthorizedBotXMethod
from pybotx.constants import SMARTAPP_API_VERSION
from pybotx.missing import Missing, MissingOptional, Undefined
from pybotx.models.api_base import UnverifiedPayloadBaseModel, VerifiedPayloadBaseModel
from pybotx.models.async_files import APIAsyncFile, File, convert_async_file_from_domain


class BotXAPISmartAppEventRequestPayload(UnverifiedPayloadBaseModel):
    ref: MissingOptional[UUID]
    smartapp_id: UUID
    group_chat_id: UUID
    data: Dict[str, Any]
    opts: Missing[Dict[str, Any]]
    smartapp_api_version: int
    async_files: Missing[List[APIAsyncFile]]
    encrypted: bool

    @classmethod
    def from_domain(
        cls,
        ref: MissingOptional[UUID],
        smartapp_id: UUID,
        chat_id: UUID,
        data: Dict[str, Any],
        opts: Missing[Dict[str, Any]],
        files: Missing[List[File]],
        encrypted: bool,
    ) -> "BotXAPISmartAppEventRequestPayload":
        api_async_files: Missing[List[APIAsyncFile]] = Undefined
        if files:
            api_async_files = [convert_async_file_from_domain(file) for file in files]

        return cls(
            ref=ref,
            smartapp_id=smartapp_id,
            group_chat_id=chat_id,
            data=data,
            opts=opts,
            smartapp_api_version=SMARTAPP_API_VERSION,
            async_files=api_async_files,
            encrypted=encrypted,
        )


class BotXAPISmartAppEventResponsePayload(VerifiedPayloadBaseModel):
    status: Literal["ok"]


class SmartAppEventMethod(AuthorizedBotXMethod):
    async def execute(
        self,
        payload: BotXAPISmartAppEventRequestPayload,
    ) -> None:
        path = "/api/v3/botx/smartapps/event"

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
            BotXAPISmartAppEventResponsePayload,
            response,
        )
