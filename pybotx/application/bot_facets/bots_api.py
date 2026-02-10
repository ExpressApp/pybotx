from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pybotx.domain.missing import Missing, Undefined
from pybotx.domain.models.bot_catalog import BotsListItem


class BotBotsApiMixin:
    async def get_token(
        self,
        *,
        bot_id: UUID,
    ) -> str:
        """Get bot auth token.

        :param bot_id: Bot which should perform the request.

        :return: Auth token.
        """
        return await self._botx_api.get_token(bot_id=bot_id)

    async def get_bots_list(
        self,
        *,
        bot_id: UUID,
        since: Missing[datetime] = Undefined,
    ) -> tuple[list[BotsListItem], datetime]:
        """Get list of Bots on the current CTS.

        :param bot_id: Bot which should perform the request.
        :param since: Only return bots changed after this date.

        :return: List of Bots, generated timestamp.
        """
        return await self._botx_api.get_bots_list(bot_id=bot_id, since=since)
