from typing import Literal

from pybotx.client.botx_method import BotXMethod, response_exception_thrower
from pybotx.client.exceptions.common import InvalidBotAccountError
from pybotx.models.api_base import UnverifiedPayloadBaseModel, VerifiedPayloadBaseModel


class BotXAPIGetTokenRequestPayload(UnverifiedPayloadBaseModel):
    signature: str

    @classmethod
    def from_domain(cls, signature: str) -> "BotXAPIGetTokenRequestPayload":
        return cls(signature=signature)


class BotXAPIGetTokenResponsePayload(VerifiedPayloadBaseModel):
    status: Literal["ok"]
    result: str

    def to_domain(self) -> str:
        return self.result


class GetTokenMethod(BotXMethod):
    status_handlers = {401: response_exception_thrower(InvalidBotAccountError)}

    async def execute(
        self,
        payload: BotXAPIGetTokenRequestPayload,
    ) -> BotXAPIGetTokenResponsePayload:
        path = f"/api/v2/botx/bots/{self._bot_id}/token"

        response = await self._botx_method_call(
            "GET",
            self._build_url(path),
            params=payload.jsonable_dict(),
        )

        return self._verify_and_extract_api_model(
            BotXAPIGetTokenResponsePayload,
            response,
        )
