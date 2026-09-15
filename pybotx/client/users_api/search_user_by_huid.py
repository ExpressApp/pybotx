from uuid import UUID

from pybotx.client.authorized_botx_method import AuthorizedBotXMethod
from pybotx.client.botx_method import response_exception_thrower
from pybotx.client.exceptions.users import UserNotFoundError
from pybotx.client.users_api.user_from_search import BotXAPISearchUserResponsePayload
from pybotx.missing import Missing, Undefined
from pybotx.models.api_base import UnverifiedPayloadBaseModel


class BotXAPISearchUserByHUIDRequestPayload(UnverifiedPayloadBaseModel):
    user_huid: UUID
    trusts_search: Missing[bool] = Undefined
    partial_response: Missing[bool] = Undefined

    @classmethod
    def from_domain(
        cls,
        huid: UUID,
        trusts_search: bool = False,
        partial_response: bool = False,
    ) -> "BotXAPISearchUserByHUIDRequestPayload":
        return cls(
            user_huid=huid,
            trusts_search=trusts_search or Undefined,
            partial_response=partial_response or Undefined,
        )


class SearchUserByHUIDMethod(AuthorizedBotXMethod):
    status_handlers = {
        **AuthorizedBotXMethod.status_handlers,
        404: response_exception_thrower(UserNotFoundError),
    }

    async def execute(
        self,
        payload: BotXAPISearchUserByHUIDRequestPayload,
    ) -> BotXAPISearchUserResponsePayload:
        path = "/api/v3/botx/users/by_huid"

        response = await self._botx_method_call(
            "GET",
            self._build_url(path),
            params=payload.jsonable_dict(),
        )

        return self._verify_and_extract_api_model(
            BotXAPISearchUserResponsePayload,
            response,
        )
