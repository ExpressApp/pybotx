from typing import List, Literal
from uuid import UUID

from pybotx.client.authorized_botx_method import AuthorizedBotXMethod
from pybotx.models.api_base import UnverifiedPayloadBaseModel, VerifiedPayloadBaseModel


class BotXAPICollectBotFunctionRequestPayload(UnverifiedPayloadBaseModel):
    group_chat_id: UUID
    user_huids: List[UUID]
    bot_function: str

    @classmethod
    def from_domain(
        cls,
        chat_id: UUID,
        huids: List[UUID],
        bot_function: str,
    ) -> "BotXAPICollectBotFunctionRequestPayload":
        return cls(group_chat_id=chat_id, user_huids=huids, bot_function=bot_function)


class BotXAPICollectBotFunctionResponsePayload(VerifiedPayloadBaseModel):
    status: Literal["ok"]
    result: bool


class CollectBotFunctionMethod(AuthorizedBotXMethod):
    async def execute(
        self,
        payload: BotXAPICollectBotFunctionRequestPayload,
    ) -> None:
        path = "/api/v3/botx/metrics/bot_function"

        response = await self._botx_method_call(
            "POST",
            self._build_url(path),
            json=payload.jsonable_dict(),
        )
        self._verify_and_extract_api_model(
            BotXAPICollectBotFunctionResponsePayload,
            response,
        )
