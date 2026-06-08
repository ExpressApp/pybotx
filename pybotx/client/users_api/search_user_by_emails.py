
from pybotx.client.authorized_botx_method import AuthorizedBotXMethod
from pybotx.client.users_api.user_from_search import (
    BotXAPISearchUserByEmailsResponsePayload,
)
from pybotx.missing import Missing, Undefined
from pybotx.models.api_base import UnverifiedPayloadBaseModel


class BotXAPISearchUserByEmailsRequestPayload(UnverifiedPayloadBaseModel):
    emails: list[str]
    trusts_search: Missing[bool] = Undefined
    partial_response: Missing[bool] = Undefined

    @classmethod
    def from_domain(
        cls,
        emails: list[str],
        trusts_search: bool = False,
        partial_response: bool = False,
    ) -> "BotXAPISearchUserByEmailsRequestPayload":
        return cls(
            emails=emails,
            trusts_search=trusts_search or Undefined,
            partial_response=partial_response or Undefined,
        )


class SearchUserByEmailsMethod(AuthorizedBotXMethod):
    async def execute(
        self,
        payload: BotXAPISearchUserByEmailsRequestPayload,
    ) -> BotXAPISearchUserByEmailsResponsePayload:
        path = "/api/v3/botx/users/by_email"

        response = await self._botx_method_call(
            "POST",
            self._build_url(path),
            json=payload.jsonable_dict(),
        )

        return self._verify_and_extract_api_model(
            BotXAPISearchUserByEmailsResponsePayload,
            response,
        )
