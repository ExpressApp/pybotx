from typing import List
from uuid import UUID

from botx.client.authorized_botx_method import AuthorizedBotXMethod
from botx.shared_models.api_base import (
    UnverifiedPayloadBaseModel,
    VerifiedPayloadBaseModel,
)

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal  # type: ignore  # noqa: WPS440


class BotXAPIAddUserRequestPayload(UnverifiedPayloadBaseModel):
    group_chat_id: UUID
    user_huids: List[UUID]

    @classmethod
    def from_domain(
        cls,
        chat_id: UUID,
        huids: List[UUID],
    ) -> "BotXAPIAddUserRequestPayload":
        return cls(group_chat_id=chat_id, user_huids=huids)


class BotXAPIAddUserResponsePayload(VerifiedPayloadBaseModel):
    status: Literal["ok"]
    result: Literal[True]


class AddUserMethod(AuthorizedBotXMethod):
    async def execute(
        self,
        payload: BotXAPIAddUserRequestPayload,
    ) -> None:
        path = "/api/v3/botx/chats/add_user"

        response = await self._botx_method_call(
            "POST",
            self._build_url(path),
            json=payload.jsonable_dict(),
        )
        self._extract_api_model(
            BotXAPIAddUserResponsePayload,
            response,
        )
