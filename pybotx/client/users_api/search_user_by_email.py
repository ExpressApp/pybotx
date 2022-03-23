from pybotx.client.authorized_botx_method import AuthorizedBotXMethod
from pybotx.client.botx_method import response_exception_thrower
from pybotx.client.exceptions.users import UserNotFoundError
from pybotx.client.users_api.user_from_search import BotXAPISearchUserResponsePayload
from pybotx.models.api_base import UnverifiedPayloadBaseModel


class BotXAPISearchUserByEmailRequestPayload(UnverifiedPayloadBaseModel):
    email: str

    @classmethod
    def from_domain(cls, email: str) -> "BotXAPISearchUserByEmailRequestPayload":
        return cls(email=email)


class SearchUserByEmailMethod(AuthorizedBotXMethod):
    status_handlers = {
        **AuthorizedBotXMethod.status_handlers,
        404: response_exception_thrower(UserNotFoundError),
    }

    async def execute(
        self,
        payload: BotXAPISearchUserByEmailRequestPayload,
    ) -> BotXAPISearchUserResponsePayload:
        path = "/api/v3/botx/users/by_email"

        response = await self._botx_method_call(
            "GET",
            self._build_url(path),
            params=payload.jsonable_dict(),
        )

        return self._verify_and_extract_api_model(
            BotXAPISearchUserResponsePayload,
            response,
        )
