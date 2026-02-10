from __future__ import annotations

from uuid import UUID


class BotMetricsMixin:
    async def collect_metric(
        self,
        bot_id: UUID,
        bot_function: str,
        huids: list[UUID],
        chat_id: UUID,
    ) -> None:
        """Collect a new use of the bot function.

        :param bot_id: Bot which should perform the request.
        :param bot_function: Name of the bot function.
        :param huids: Users involved in using the function.
        :param chat_id: Chat in which the function was used.
        """
        await self._botx_api.collect_metric(
            bot_id=bot_id,
            bot_function=bot_function,
            huids=huids,
            chat_id=chat_id,
        )
