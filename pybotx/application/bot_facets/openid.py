from __future__ import annotations

from uuid import UUID


class BotOpenIdMixin:
    async def refresh_access_token(
        self,
        *,
        bot_id: UUID,
        huid: UUID,
        ref: UUID | None = None,
    ) -> None:
        """Refresh OpenID access token.

        :param bot_id: Bot which should perform the request.
        :param huid: User huid.
        :param ref: sync_id of the failed event to resend.
        """
        await self._botx_api.refresh_access_token(bot_id=bot_id, huid=huid, ref=ref)
