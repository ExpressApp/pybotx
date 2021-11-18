from uuid import UUID

from botx.client.authorized_botx_method import AuthorizedBotXMethod
from botx.client.botx_method import response_exception_thrower
from botx.client.exceptions.common import ChatNotFoundError, PermissionDeniedError
from botx.missing import Missing
from botx.shared_models.api_base import (
    UnverifiedPayloadBaseModel,
    VerifiedPayloadBaseModel,
)

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal  # type: ignore  # noqa: WPS440


class BotXAPISetStealthRequestPayload(UnverifiedPayloadBaseModel):
    group_chat_id: UUID
    disable_web: bool
    burn_in: Missing[int]
    expire_in: Missing[int]

    @classmethod
    def from_domain(
        cls,
        chat_id: UUID,
        disable_in_web_client: bool,
        ttl_after_read: Missing[int],
        total_ttl: Missing[int],
    ) -> "BotXAPISetStealthRequestPayload":
        return cls(
            group_chat_id=chat_id,
            disable_web=disable_in_web_client,
            burn_in=ttl_after_read,
            expire_in=total_ttl,
        )


class BotXAPISetStealthResponsePayload(VerifiedPayloadBaseModel):
    status: Literal["ok"]
    result: Literal[True]


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