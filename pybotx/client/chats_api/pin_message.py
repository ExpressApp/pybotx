from typing import Literal
from uuid import UUID

from pybotx.client.authorized_botx_method import AuthorizedBotXMethod
from pybotx.client.botx_method import response_exception_thrower
from pybotx.client.exceptions.common import ChatNotFoundError, PermissionDeniedError
from pybotx.models.api_base import UnverifiedPayloadBaseModel, VerifiedPayloadBaseModel


class BotXAPIPinMessageRequestPayload(UnverifiedPayloadBaseModel):
    chat_id: UUID
    sync_id: UUID

    @classmethod
    def from_domain(
        cls,
        chat_id: UUID,
        sync_id: UUID,
    ) -> "BotXAPIPinMessageRequestPayload":
        return cls(chat_id=chat_id, sync_id=sync_id)


class BotXAPIPinMessageResponsePayload(VerifiedPayloadBaseModel):
    status: Literal["ok"]


class PinMessageMethod(AuthorizedBotXMethod):
    status_handlers = {
        **AuthorizedBotXMethod.status_handlers,
        403: response_exception_thrower(PermissionDeniedError),
        404: response_exception_thrower(ChatNotFoundError),
    }

    async def execute(
        self,
        payload: BotXAPIPinMessageRequestPayload,
    ) -> None:
        path = "/api/v3/botx/chats/pin_message"

        response = await self._botx_method_call(
            "POST",
            self._build_url(path),
            json=payload.jsonable_dict(),
        )

        self._verify_and_extract_api_model(BotXAPIPinMessageResponsePayload, response)
