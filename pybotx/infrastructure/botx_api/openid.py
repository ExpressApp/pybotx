from __future__ import annotations

from uuid import UUID

from pybotx.infrastructure.client.openid_api.refresh_access_token import (
    BotXAPIRefreshAccessTokenRequestPayload,
    RefreshAccessTokenMethod,
)


class OpenIdApiMixin:
    async def refresh_access_token(
        self,
        *,
        bot_id: UUID,
        huid: UUID,
        ref: UUID | None = None,
    ) -> None:
        method = self._method_factory.build(RefreshAccessTokenMethod, bot_id=bot_id)
        payload = BotXAPIRefreshAccessTokenRequestPayload.from_domain(
            huid=huid,
            ref=ref,
        )
        await method.execute(payload)
