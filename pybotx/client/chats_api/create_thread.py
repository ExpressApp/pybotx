import typing
from typing import Literal
from uuid import UUID

from pybotx.client.authorized_botx_method import AuthorizedBotXMethod
from pybotx.client.botx_method import response_exception_thrower
from pybotx.client.exceptions.chats import (
    ThreadCreationError,
    ThreadCreationEventNotFoundError,
    ThreadCreationProhibitedError,
)
from pybotx.models.api_base import UnverifiedPayloadBaseModel, VerifiedPayloadBaseModel


class BotXAPICreateThreadRequestPayload(UnverifiedPayloadBaseModel):
    sync_id: UUID

    @classmethod
    def from_domain(cls, sync_id: UUID) -> "BotXAPICreateThreadRequestPayload":
        return cls(sync_id=sync_id)


class BotXAPIThreadIdResult(VerifiedPayloadBaseModel):
    thread_id: UUID


class BotXAPICreateThreadResponsePayload(VerifiedPayloadBaseModel):
    status: Literal["ok"]
    result: BotXAPIThreadIdResult

    def to_domain(self) -> UUID:
        return self.result.thread_id


class CreateThreadMethod(AuthorizedBotXMethod):
    status_handlers = {
        **AuthorizedBotXMethod.status_handlers,
        403: response_exception_thrower(ThreadCreationProhibitedError),
        404: response_exception_thrower(ThreadCreationEventNotFoundError),
        422: response_exception_thrower(ThreadCreationError),
    }

    async def execute(
        self,
        payload: BotXAPICreateThreadRequestPayload,
    ) -> BotXAPICreateThreadResponsePayload:
        path = "/api/v3/botx/chats/create_thread"

        response = await self._botx_method_call(
            "POST",
            self._build_url(path),
            json=payload.jsonable_dict(),
        )

        return self._verify_and_extract_api_model(
            BotXAPICreateThreadResponsePayload,
            response,
        )
