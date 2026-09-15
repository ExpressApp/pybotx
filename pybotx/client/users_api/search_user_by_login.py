from pybotx.client.authorized_botx_method import AuthorizedBotXMethod
from pybotx.client.botx_method import response_exception_thrower
from pybotx.client.exceptions.users import UserNotFoundError
from pybotx.client.users_api.user_from_search import BotXAPISearchUserResponsePayload
from pybotx.client.users_api.trusted_search import validate_trusted_search_options
from pybotx.missing import Missing, Undefined
from pybotx.models.api_base import UnverifiedPayloadBaseModel


class BotXAPISearchUserByLoginRequestPayload(UnverifiedPayloadBaseModel):
    ad_login: str
    ad_domain: str
    trusts_search: Missing[bool] = Undefined
    partial_response: Missing[bool] = Undefined

    @classmethod
    def from_domain(
        cls,
        ad_login: str,
        ad_domain: str,
        trusts_search: bool = False,
        partial_response: bool = False,
    ) -> "BotXAPISearchUserByLoginRequestPayload":
        validate_trusted_search_options(
            trusts_search=trusts_search,
            partial_response=partial_response,
        )
        return cls(
            ad_login=ad_login,
            ad_domain=ad_domain,
            trusts_search=trusts_search or Undefined,
            partial_response=partial_response or Undefined,
        )


class SearchUserByLoginMethod(AuthorizedBotXMethod):
    status_handlers = {
        **AuthorizedBotXMethod.status_handlers,
        404: response_exception_thrower(UserNotFoundError),
    }

    async def execute(
        self,
        payload: BotXAPISearchUserByLoginRequestPayload,
    ) -> BotXAPISearchUserResponsePayload:
        path = "/api/v3/botx/users/by_login"

        response = await self._botx_method_call(
            "GET",
            self._build_url(path),
            params=payload.jsonable_dict(),
        )

        return self._verify_and_extract_api_model(
            BotXAPISearchUserResponsePayload,
            response,
        )
