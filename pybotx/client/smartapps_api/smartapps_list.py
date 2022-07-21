from typing import List, Literal, Optional, Tuple
from uuid import UUID

from pybotx.client.authorized_botx_method import AuthorizedBotXMethod
from pybotx.missing import Missing, Undefined
from pybotx.models.api_base import UnverifiedPayloadBaseModel, VerifiedPayloadBaseModel
from pybotx.models.smartapps import SmartApp


class BotXAPISmartAppsListRequestPayload(UnverifiedPayloadBaseModel):
    version: Missing[int] = Undefined

    @classmethod
    def from_domain(
        cls,
        version: Missing[int] = Undefined,
    ) -> "BotXAPISmartAppsListRequestPayload":
        return cls(version=version)


class BotXAPISmartAppEntity(VerifiedPayloadBaseModel):
    app_id: str
    enabled: bool
    id: UUID
    name: str
    avatar: Optional[str] = None
    avatar_preview: Optional[str] = None


class BotXAPISmartAppsListResult(VerifiedPayloadBaseModel):
    phonebook_version: int
    smartapps: List[BotXAPISmartAppEntity]


class BotXAPISmartAppsListResponsePayload(VerifiedPayloadBaseModel):
    result: BotXAPISmartAppsListResult
    status: Literal["ok"]

    def to_domain(self) -> Tuple[List[SmartApp], int]:
        smartapps_list = [
            SmartApp(
                app_id=smartapp.app_id,
                enabled=smartapp.enabled,
                id=smartapp.id,
                name=smartapp.name,
                avatar=smartapp.avatar,
                avatar_preview=smartapp.avatar_preview,
            )
            for smartapp in self.result.smartapps
        ]
        return (
            smartapps_list,
            self.result.phonebook_version,
        )


class SmartAppsListMethod(AuthorizedBotXMethod):
    status_handlers = {
        **AuthorizedBotXMethod.status_handlers,
    }

    async def execute(
        self,
        payload: BotXAPISmartAppsListRequestPayload,
    ) -> BotXAPISmartAppsListResponsePayload:
        path = "/api/v3/botx/smartapps/list"

        response = await self._botx_method_call(
            "GET",
            self._build_url(path),
            params=payload.jsonable_dict(),
        )

        return self._verify_and_extract_api_model(
            BotXAPISmartAppsListResponsePayload,
            response,
        )
