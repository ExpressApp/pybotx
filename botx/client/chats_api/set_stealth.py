from typing import Optional
from uuid import UUID

from botx.client.authorized_botx_method import AuthorizedBotXMethod
from botx.client.botx_method import response_exception_thrower
from botx.client.exceptions.common import ChatNotFoundError, PermissionDeniedError
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
    burn_in: Optional[int]
    expire_in: Optional[int]

    @classmethod
    def from_domain(
        cls,
        chat_id: UUID,
        is_disable_web: bool,
        active_time_for_read: Optional[int],
        active_time: Optional[int],
    ) -> "BotXAPISetStealthRequestPayload":
        return cls(
            group_chat_id=chat_id,
            disable_web=is_disable_web,
            burn_in=active_time_for_read,
            expire_in=active_time,
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

        self._extract_api_model(BotXAPISetStealthResponsePayload, response)
