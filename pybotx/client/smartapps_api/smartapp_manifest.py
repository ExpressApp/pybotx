from typing import List, Literal
from uuid import UUID

from pydantic import Field

from pybotx.client.authorized_botx_method import AuthorizedBotXMethod
from pybotx.missing import Missing, Undefined
from pybotx.models.api_base import UnverifiedPayloadBaseModel, VerifiedPayloadBaseModel
from pybotx.models.enums import SmartappManifestWebLayoutChoices as WebLayoutChoices


class SmartappManifestIosParams(VerifiedPayloadBaseModel):
    fullscreen_layout: bool = False


class SmartappManifestAndroidParams(VerifiedPayloadBaseModel):
    fullscreen_layout: bool = False


class SmartappManifestAuroraParams(VerifiedPayloadBaseModel):
    fullscreen_layout: bool = False


class SmartappManifestWebParams(VerifiedPayloadBaseModel):
    default_layout: WebLayoutChoices = WebLayoutChoices.minimal
    expanded_layout: WebLayoutChoices = WebLayoutChoices.half
    always_pinned: bool = False


class SmartappManifestUnreadCounterParams(VerifiedPayloadBaseModel):
    user_huid: List[UUID] = Field(default_factory=list)
    group_chat_id: List[UUID] = Field(default_factory=list)
    app_id: List[str] = Field(default_factory=list)


class SmartappManifest(VerifiedPayloadBaseModel):
    ios: SmartappManifestIosParams
    android: SmartappManifestAndroidParams
    web: SmartappManifestWebParams
    unread_counter_link: SmartappManifestUnreadCounterParams


class SmartappManifestPayload(UnverifiedPayloadBaseModel):
    ios: Missing[SmartappManifestIosParams] = Undefined
    android: Missing[SmartappManifestAndroidParams] = Undefined
    web: Missing[SmartappManifestWebParams] = Undefined
    aurora: Missing[SmartappManifestAuroraParams] = Undefined
    unread_counter_link: Missing[SmartappManifestUnreadCounterParams] = Undefined


class BotXAPISmartAppManifestRequestPayload(UnverifiedPayloadBaseModel):
    manifest: SmartappManifestPayload

    @classmethod
    def from_domain(
        cls,
        ios: Missing[SmartappManifestIosParams] = Undefined,
        android: Missing[SmartappManifestAndroidParams] = Undefined,
        web_layout: Missing[SmartappManifestWebParams] = Undefined,
        unread_counter: Missing[SmartappManifestUnreadCounterParams] = Undefined,
    ) -> "BotXAPISmartAppManifestRequestPayload":
        if web_layout is Undefined and unread_counter is Undefined:
            return cls(manifest={})

        return cls(
            manifest=SmartappManifestPayload(
                ios=ios,
                android=android,
                web=web_layout,
                unread_counter_link=unread_counter,
            ),
        )


class BotXAPISmartAppManifestResponsePayload(VerifiedPayloadBaseModel):
    status: Literal["ok"]
    result: SmartappManifest

    def to_domain(self) -> SmartappManifest:
        return self.result


class SmartAppManifestMethod(AuthorizedBotXMethod):
    async def execute(
        self,
        payload: BotXAPISmartAppManifestRequestPayload,
    ) -> BotXAPISmartAppManifestResponsePayload:
        path = "/api/v1/botx/smartapps/manifest"

        response = await self._botx_method_call(
            "POST",
            self._build_url(path),
            json=payload.jsonable_dict(),
        )

        return self._verify_and_extract_api_model(
            BotXAPISmartAppManifestResponsePayload,
            response,
        )
