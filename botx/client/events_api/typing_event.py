from uuid import UUID

from typing_extensions import Literal  # For python 3.7 support

from botx.client.authorized_botx_method import AuthorizedBotXMethod
from botx.models.api_base import UnverifiedPayloadBaseModel, VerifiedPayloadBaseModel


class BotXAPITypingEventRequestPayload(UnverifiedPayloadBaseModel):
    group_chat_id: UUID

    @classmethod
    def from_domain(cls, chat_id: UUID) -> "BotXAPITypingEventRequestPayload":
        return cls(group_chat_id=chat_id)


class BotXAPITypingEventResponsePayload(VerifiedPayloadBaseModel):
    status: Literal["ok"]


class TypingEventMethod(AuthorizedBotXMethod):
    async def execute(self, payload: BotXAPITypingEventRequestPayload) -> None:
        path = "/api/v3/botx/events/typing"

        response = await self._botx_method_call(
            "POST",
            self._build_url(path),
            json=payload.jsonable_dict(),
        )

        self._verify_and_extract_api_model(BotXAPITypingEventResponsePayload, response)
