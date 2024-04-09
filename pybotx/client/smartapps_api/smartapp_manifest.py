from typing import Literal

from pybotx.client.authorized_botx_method import AuthorizedBotXMethod
from pybotx.models.api_base import VerifiedPayloadBaseModel
from pybotx.models.enums import SmartappManifestWebLayoutChoices as WebLayoutChoices


class SmartappManifestWebParams(VerifiedPayloadBaseModel):
    default_layout: WebLayoutChoices = WebLayoutChoices.minimal
    expanded_layout: WebLayoutChoices = WebLayoutChoices.half
    always_pinned: bool = False


class SmartappManifest(VerifiedPayloadBaseModel):
    web: SmartappManifestWebParams


class BotXAPISmartAppManifestRequestPayload(VerifiedPayloadBaseModel):
    manifest: SmartappManifest

    @classmethod
    def from_domain(
        cls,
        web_default_layout: WebLayoutChoices = WebLayoutChoices.minimal,
        web_expanded_layout: WebLayoutChoices = WebLayoutChoices.half,
        web_always_pinned: bool = False,
    ) -> "BotXAPISmartAppManifestRequestPayload":
        return cls(
            manifest=SmartappManifest(
                web=SmartappManifestWebParams(
                    default_layout=web_default_layout,
                    expanded_layout=web_expanded_layout,
                    always_pinned=web_always_pinned,
                ),
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
