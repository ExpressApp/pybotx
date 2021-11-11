from botx.client.authorized_botx_method import AuthorizedBotXMethod
from botx.client.botx_method import response_exception_thrower
from botx.client.users_api.exceptions import UserNotFoundError
from botx.client.users_api.models import BotXAPISearchUserResponsePayload
from botx.shared_models.api_base import UnverifiedPayloadBaseModel


class BotXAPISearchUserByLoginRequestPayload(UnverifiedPayloadBaseModel):
    ad_login: str
    ad_domain: str

    @classmethod
    def from_domain(
        cls,
        ad_login: str,
        ad_domain: str,
    ) -> "BotXAPISearchUserByLoginRequestPayload":
        return cls(ad_login=ad_login, ad_domain=ad_domain)


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

        return self._extract_api_model(BotXAPISearchUserResponsePayload, response)
