from typing import Literal
from uuid import UUID

from pybotx.client.authorized_botx_method import AuthorizedBotXMethod
from pybotx.client.botx_method import response_exception_thrower
from pybotx.client.exceptions.common import ChatNotFoundError, PermissionDeniedError
from pybotx.missing import Missing
from pybotx.models.api_base import UnverifiedPayloadBaseModel, VerifiedPayloadBaseModel


class BotXAPISetStealthRequestPayload(UnverifiedPayloadBaseModel):
    group_chat_id: UUID
    disable_web: Missing[bool]
    burn_in: Missing[int]
    expire_in: Missing[int]

    @classmethod
    def from_domain(
        cls,
        chat_id: UUID,
        disable_web_client: Missing[bool],
        ttl_after_read: Missing[int],
        total_ttl: Missing[int],
    ) -> "BotXAPISetStealthRequestPayload":
        return cls(
            group_chat_id=chat_id,
            disable_web=disable_web_client,
            burn_in=ttl_after_read,
            expire_in=total_ttl,
        )


class BotXAPISetStealthResponsePayload(VerifiedPayloadBaseModel):
    status: Literal["ok"]


class SetStealthMethod(AuthorizedBotXMethod):
    status_handlers = {
        **AuthorizedBotXMethod.status_handlers,
        403: response_exception_thrower(PermissionDeniedError),
        404: response_exception_thrower(ChatNotFoundError),
    }

    async def execute(self, payload: BotXAPISetStealthRequestPayload) -> None:
        path = "/api/v3/botx/chats/stealth_set"

        response = await self._botx_method_call(
            "POST",
            self._build_url(path),
            json=payload.jsonable_dict(),
        )

        self._verify_and_extract_api_model(BotXAPISetStealthResponsePayload, response)
