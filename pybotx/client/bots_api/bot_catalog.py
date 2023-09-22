from datetime import datetime
from typing import List, Literal, Optional, Tuple
from uuid import UUID

from pybotx.client.authorized_botx_method import AuthorizedBotXMethod
from pybotx.missing import Missing, Undefined
from pybotx.models.api_base import UnverifiedPayloadBaseModel, VerifiedPayloadBaseModel
from pybotx.models.bot_catalog import BotsListItem


class BotXAPIBotsListRequestPayload(UnverifiedPayloadBaseModel):
    since: Missing[datetime] = Undefined

    @classmethod
    def from_domain(
        cls,
        since: Missing[datetime] = Undefined,
    ) -> "BotXAPIBotsListRequestPayload":
        return cls(since=since)


class BotXAPIBotItem(VerifiedPayloadBaseModel):
    user_huid: UUID
    name: str
    description: str
    avatar: Optional[str] = None
    enabled: bool


class BotXAPIBotsListResult(VerifiedPayloadBaseModel):
    generated_at: datetime
    bots: List[BotXAPIBotItem]


class BotXAPIBotsListResponsePayload(VerifiedPayloadBaseModel):
    result: BotXAPIBotsListResult
    status: Literal["ok"]

    def to_domain(self) -> Tuple[List[BotsListItem], datetime]:
        bots_list = [
            BotsListItem(
                id=bot.user_huid,
                name=bot.name,
                description=bot.description,
                avatar=bot.avatar,
                enabled=bot.enabled,
            )
            for bot in self.result.bots
        ]
        return bots_list, self.result.generated_at


class BotsListMethod(AuthorizedBotXMethod):
    async def execute(
        self,
        payload: BotXAPIBotsListRequestPayload,
    ) -> BotXAPIBotsListResponsePayload:
        path = "/api/v1/botx/bots/catalog"

        response = await self._botx_method_call(
            "GET",
            self._build_url(path),
            params=payload.jsonable_dict(),
        )

        return self._verify_and_extract_api_model(
            BotXAPIBotsListResponsePayload,
            response,
        )
