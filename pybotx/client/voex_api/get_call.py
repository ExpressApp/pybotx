from typing import Literal
from uuid import UUID

from pybotx.client.authorized_botx_method import AuthorizedBotXMethod
from pybotx.client.botx_method import response_exception_thrower
from pybotx.client.voex_api.exceptions import CallNotFoundError
from pybotx.models.api_base import UnverifiedPayloadBaseModel, VerifiedPayloadBaseModel
from pybotx.models.call import Call


class BotXAPIGetCallRequestPayload(UnverifiedPayloadBaseModel):
    call_id: UUID

    @classmethod
    def from_domain(
        cls,
        call_id: UUID,
    ) -> "BotXAPIGetCallRequestPayload":
        return cls(call_id=call_id)


class BotXAPIGetCallResult(VerifiedPayloadBaseModel):
    id: UUID
    members: list[UUID]


class BotXAPIGetCallResponsePayload(VerifiedPayloadBaseModel):
    status: Literal["ok"]
    result: BotXAPIGetCallResult

    def to_domain(self) -> Call:
        return Call(
            id=self.result.id,
            members=self.result.members,
        )


class GetCallMethod(AuthorizedBotXMethod):
    status_handlers = {
        **AuthorizedBotXMethod.status_handlers,
        404: response_exception_thrower(CallNotFoundError),
    }

    async def execute(
        self,
        payload: BotXAPIGetCallRequestPayload,
    ) -> BotXAPIGetCallResponsePayload:
        jsonable_dict = payload.jsonable_dict()
        path = f"/api/v3/botx/voex/calls/{jsonable_dict['call_id']}"

        response = await self._botx_method_call(
            "GET",
            self._build_url(path),
        )

        return self._verify_and_extract_api_model(
            BotXAPIGetCallResponsePayload,
            response,
        )
