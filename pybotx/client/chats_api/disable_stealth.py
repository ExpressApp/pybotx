from typing import Literal
from uuid import UUID

from pybotx.client.authorized_botx_method import AuthorizedBotXMethod
from pybotx.client.botx_method import response_exception_thrower
from pybotx.client.exceptions.common import ChatNotFoundError, PermissionDeniedError
from pybotx.models.api_base import UnverifiedPayloadBaseModel, VerifiedPayloadBaseModel


class BotXAPIDisableStealthRequestPayload(UnverifiedPayloadBaseModel):
    group_chat_id: UUID

    @classmethod
    def from_domain(
        cls,
        chat_id: UUID,
    ) -> "BotXAPIDisableStealthRequestPayload":
        return cls(
            group_chat_id=chat_id,
        )


class BotXAPIDisableStealthResponsePayload(VerifiedPayloadBaseModel):
    status: Literal["ok"]


class DisableStealthMethod(AuthorizedBotXMethod):
    status_handlers = {
        **AuthorizedBotXMethod.status_handlers,
        403: response_exception_thrower(PermissionDeniedError),
        404: response_exception_thrower(ChatNotFoundError),
    }

    async def execute(self, payload: BotXAPIDisableStealthRequestPayload) -> None:
        path = "/api/v3/botx/chats/stealth_disable"

        response = await self._botx_method_call(
            "POST",
            self._build_url(path),
            json=payload.jsonable_dict(),
        )

        self._verify_and_extract_api_model(
            BotXAPIDisableStealthResponsePayload,
            response,
        )
