from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pybotx.domain.missing import Missing, Undefined
from pybotx.domain.models.bot_catalog import BotsListItem
from pybotx.infrastructure.client.bots_api.bot_catalog import (
    BotsListMethod,
    BotXAPIBotsListRequestPayload,
)
from pybotx.infrastructure.client.get_token import get_token


class BotsApiMixin:
    async def get_token(self, *, bot_id: UUID) -> str:
        return await get_token(bot_id, self._http_client, self._bot_accounts_storage)

    async def get_bots_list(
        self,
        *,
        bot_id: UUID,
        since: Missing[datetime] = Undefined,
    ) -> tuple[list[BotsListItem], datetime]:
        method = self._method_factory.build(BotsListMethod, bot_id=bot_id)
        payload = BotXAPIBotsListRequestPayload.from_domain(since=since)
        botx_api_bots_list = await method.execute(payload)
        return botx_api_bots_list.to_domain()
