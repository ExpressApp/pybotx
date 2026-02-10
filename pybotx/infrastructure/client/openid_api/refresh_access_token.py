from typing import Literal
from uuid import UUID

from pybotx.infrastructure.client.authorized_botx_method import AuthorizedBotXMethod
from pybotx.domain.models.api_base import (
    UnverifiedPayloadBaseModel,
    VerifiedPayloadBaseModel,
)


class BotXAPIRefreshAccessTokenRequestPayload(UnverifiedPayloadBaseModel):
    user_huid: UUID
    ref: UUID | None

    @classmethod
    def from_domain(
        cls,
        huid: UUID,
        ref: UUID | None,
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
