from typing import Literal, NoReturn
from uuid import UUID

import httpx

from pybotx.client.authorized_botx_method import AuthorizedBotXMethod
from pybotx.client.botx_method import response_exception_thrower
from pybotx.client.exceptions.chats import (
    ThreadAlreadyExistsError,
    ThreadCreationError,
    ThreadCreationProhibitedError,
)
from pybotx.client.exceptions.event import EventNotFoundError
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


def conflict_error_handler(response: httpx.Response) -> NoReturn:
    reason = response.json().get("reason")

    if reason == "thread_already_created":
        raise ThreadAlreadyExistsError.from_response(response)

    raise ThreadCreationError.from_response(response)


class CreateThreadMethod(AuthorizedBotXMethod):
    status_handlers = {
        **AuthorizedBotXMethod.status_handlers,
        403: response_exception_thrower(ThreadCreationProhibitedError),
        404: response_exception_thrower(EventNotFoundError),
        409: conflict_error_handler,
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
