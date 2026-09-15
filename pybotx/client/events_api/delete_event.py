from typing import Literal
from uuid import UUID

from pybotx.client.authorized_botx_method import AuthorizedBotXMethod
from pybotx.client.botx_method import response_exception_thrower
from pybotx.client.exceptions.message import MessageNotFoundError
from pybotx.models.api_base import UnverifiedPayloadBaseModel, VerifiedPayloadBaseModel


class BotXAPIDeleteEventRequestPayload(UnverifiedPayloadBaseModel):
    sync_id: UUID

    @classmethod
    def from_domain(
        cls,
        sync_id: UUID,
    ) -> "BotXAPIDeleteEventRequestPayload":
        return cls(sync_id=sync_id)


class BotXAPIDeleteEventResponsePayload(VerifiedPayloadBaseModel):
    status: Literal["ok"]
    result: str


class DeleteEventMethod(AuthorizedBotXMethod):
    status_handlers = {
        **AuthorizedBotXMethod.status_handlers,
        404: response_exception_thrower(MessageNotFoundError),
    }

    async def execute(
        self,
        payload: BotXAPIDeleteEventRequestPayload,
    ) -> BotXAPIDeleteEventResponsePayload:
        path = "/api/v3/botx/events/delete_event"

        response = await self._botx_method_call(
            "POST",
            self._build_url(path),
            json=payload.jsonable_dict(),
        )

        return self._verify_and_extract_api_model(
            BotXAPIDeleteEventResponsePayload,
            response,
        )
