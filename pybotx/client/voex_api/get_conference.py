from typing import Literal
from uuid import UUID

from pybotx.client.authorized_botx_method import AuthorizedBotXMethod
from pybotx.client.botx_method import response_exception_thrower
from pybotx.client.voex_api.exceptions import ConferenceNotFoundError
from pybotx.models.api_base import UnverifiedPayloadBaseModel, VerifiedPayloadBaseModel
from pybotx.models.conference import Conference


class BotXAPIGetConferenceRequestPayload(UnverifiedPayloadBaseModel):
    call_id: UUID

    @classmethod
    def from_domain(
        cls,
        call_id: UUID,
    ) -> "BotXAPIGetConferenceRequestPayload":
        return cls(call_id=call_id)


class BotXAPIGetConferenceResult(VerifiedPayloadBaseModel):
    id: UUID
    name: str
    link: str
    members: list[UUID]


class BotXAPIGetConferenceResponsePayload(VerifiedPayloadBaseModel):
    status: Literal["ok"]
    result: BotXAPIGetConferenceResult

    def to_domain(self) -> Conference:
        return Conference(
            id=self.result.id,
            name=self.result.name,
            link=self.result.link,
            members=self.result.members,
        )


class GetConferenceMethod(AuthorizedBotXMethod):
    status_handlers = {
        **AuthorizedBotXMethod.status_handlers,
        404: response_exception_thrower(ConferenceNotFoundError),
    }

    async def execute(
        self,
        payload: BotXAPIGetConferenceRequestPayload,
    ) -> BotXAPIGetConferenceResponsePayload:
        jsonable_dict = payload.jsonable_dict()
        path = f"/api/v3/botx/voex/conferences/{jsonable_dict['call_id']}"

        response = await self._botx_method_call(
            "GET",
            self._build_url(path),
        )

        return self._verify_and_extract_api_model(
            BotXAPIGetConferenceResponsePayload,
            response,
        )
