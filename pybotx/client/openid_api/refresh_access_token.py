from typing import Literal, Optional
from uuid import UUID

from pybotx.client.authorized_botx_method import AuthorizedBotXMethod
from pybotx.models.api_base import UnverifiedPayloadBaseModel, VerifiedPayloadBaseModel


class BotXAPIRefreshAccessTokenRequestPayload(UnverifiedPayloadBaseModel):
    user_huid: UUID
    ref: Optional[UUID]

    @classmethod
    def from_domain(
        cls,
        huid: UUID,
        ref: Optional[UUID],
    ) -> "BotXAPIRefreshAccessTokenRequestPayload":
        return cls(
            user_huid=huid,
            ref=ref,
        )


class BotXAPIRefreshAccessTokenResponsePayload(VerifiedPayloadBaseModel):
    status: Literal["ok"]
    result: bool


class RefreshAccessTokenMethod(AuthorizedBotXMethod):
    async def execute(
        self,
        payload: BotXAPIRefreshAccessTokenRequestPayload,
    ) -> BotXAPIRefreshAccessTokenResponsePayload:
        path = "/api/v3/botx/openid/refresh_access_token"

        response = await self._botx_method_call(
            "POST",
            self._build_url(path),
            json=payload.jsonable_dict(),
        )

        return self._verify_and_extract_api_model(
            BotXAPIRefreshAccessTokenResponsePayload,
            response,
        )
