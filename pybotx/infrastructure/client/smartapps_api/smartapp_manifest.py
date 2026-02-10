from typing import Literal

from pybotx.infrastructure.client.authorized_botx_method import AuthorizedBotXMethod
from pybotx.domain.missing import Missing, Undefined
from pybotx.domain.models.api_base import (
    UnverifiedPayloadBaseModel,
    VerifiedPayloadBaseModel,
)
from pybotx.domain.models.smartapp_manifest import (
    SmartappManifest,
    SmartappManifestAndroidParams,
    SmartappManifestIosParams,
    SmartappManifestUnreadCounterParams,
    SmartappManifestWebParams,
)
from pybotx.infrastructure.contracts.smartapp_manifest import (
    SmartappManifest as SmartappManifestDTO,
    SmartappManifestAndroidParams as SmartappManifestAndroidParamsDTO,
    SmartappManifestIosParams as SmartappManifestIosParamsDTO,
    SmartappManifestPayload,
    SmartappManifestUnreadCounterParams as SmartappManifestUnreadCounterParamsDTO,
    SmartappManifestWebParams as SmartappManifestWebParamsDTO,
)


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

        ios_payload: Missing[SmartappManifestIosParamsDTO] = Undefined
        if ios is not Undefined:
            ios_payload = SmartappManifestIosParamsDTO.from_domain(ios)

        android_payload: Missing[SmartappManifestAndroidParamsDTO] = Undefined
        if android is not Undefined:
            android_payload = SmartappManifestAndroidParamsDTO.from_domain(android)

        web_payload: Missing[SmartappManifestWebParamsDTO] = Undefined
        if web_layout is not Undefined:
            web_payload = SmartappManifestWebParamsDTO.from_domain(web_layout)

        unread_payload: Missing[SmartappManifestUnreadCounterParamsDTO] = Undefined
        if unread_counter is not Undefined:
            unread_payload = SmartappManifestUnreadCounterParamsDTO.from_domain(
                unread_counter
            )

        return cls(
            manifest=SmartappManifestPayload(
                ios=ios_payload,
                android=android_payload,
                web=web_payload,
                unread_counter_link=unread_payload,
            ),
        )


class BotXAPISmartAppManifestResponsePayload(VerifiedPayloadBaseModel):
    status: Literal["ok"]
    result: SmartappManifestDTO

    def to_domain(self) -> SmartappManifest:
        return self.result.to_domain()


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
