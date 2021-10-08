from typing import NoReturn

import httpx

from botx.client.botx_method import BotXMethod
from botx.client.exceptions.common import InvalidBotAccountError
from botx.shared_models.api_base import (
    UnverifiedPayloadBaseModel,
    VerifiedPayloadBaseModel,
)

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal  # type: ignore  # noqa: WPS440


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


def invalid_bot_account_error_status_handler(response: httpx.Response) -> NoReturn:
    raise InvalidBotAccountError(response)


class GetTokenMethod(BotXMethod):
    status_handlers = {401: invalid_bot_account_error_status_handler}

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

        return self._extract_api_model(BotXAPIGetTokenResponsePayload, response)
