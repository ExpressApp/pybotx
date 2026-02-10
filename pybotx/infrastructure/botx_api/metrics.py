from __future__ import annotations

from uuid import UUID

from pybotx.infrastructure.client.mertics_api.collect_bot_function import (
    BotXAPICollectBotFunctionRequestPayload,
    CollectBotFunctionMethod,
)


class MetricsApiMixin:
    async def collect_metric(
        self,
        bot_id: UUID,
        bot_function: str,
        huids: list[UUID],
        chat_id: UUID,
    ) -> None:
        method = self._method_factory.build(CollectBotFunctionMethod, bot_id=bot_id)
        payload = BotXAPICollectBotFunctionRequestPayload.from_domain(
            bot_function=bot_function,
            huids=huids,
            chat_id=chat_id,
        )
        await method.execute(payload)
