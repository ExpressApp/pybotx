from botx.client.authorized_botx_method import AuthorizedBotXMethod
from botx.client.botx_method import response_exception_thrower
from botx.client.users_api.exceptions import UserNotFoundError
from botx.client.users_api.user_from_search import BotXAPISearchUserResponsePayload
from botx.shared_models.api_base import UnverifiedPayloadBaseModel


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

        return self._extract_api_model(BotXAPISearchUserResponsePayload, response)
