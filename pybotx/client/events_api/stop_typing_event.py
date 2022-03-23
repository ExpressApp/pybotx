from typing import Literal
from uuid import UUID

from pybotx.client.authorized_botx_method import AuthorizedBotXMethod
from pybotx.models.api_base import UnverifiedPayloadBaseModel, VerifiedPayloadBaseModel


class BotXAPIStopTypingEventRequestPayload(UnverifiedPayloadBaseModel):
    group_chat_id: UUID

    @classmethod
    def from_domain(cls, chat_id: UUID) -> "BotXAPIStopTypingEventRequestPayload":
        return cls(group_chat_id=chat_id)


class BotXAPIStopTypingEventResponsePayload(VerifiedPayloadBaseModel):
    status: Literal["ok"]


class StopTypingEventMethod(AuthorizedBotXMethod):
    async def execute(self, payload: BotXAPIStopTypingEventRequestPayload) -> None:
        path = "/api/v3/botx/events/stop_typing"

        response = await self._botx_method_call(
            "POST",
            self._build_url(path),
            json=payload.jsonable_dict(),
        )

        self._verify_and_extract_api_model(
            BotXAPIStopTypingEventResponsePayload,
            response,
        )
