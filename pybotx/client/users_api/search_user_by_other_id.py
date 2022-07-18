from pybotx.client.authorized_botx_method import AuthorizedBotXMethod
from pybotx.client.botx_method import response_exception_thrower
from pybotx.client.exceptions.users import UserNotFoundError
from pybotx.client.users_api.user_from_search import BotXAPISearchUserResponsePayload
from pybotx.models.api_base import UnverifiedPayloadBaseModel


class BotXAPISearchUserByOtherIdRequestPayload(UnverifiedPayloadBaseModel):
    other_id: str

    @classmethod
    def from_domain(cls, other_id: str) -> "BotXAPISearchUserByOtherIdRequestPayload":
        return cls(other_id=other_id)


class SearchUserByOtherIdMethod(AuthorizedBotXMethod):
    status_handlers = {
        **AuthorizedBotXMethod.status_handlers,
        404: response_exception_thrower(UserNotFoundError),
    }

    async def execute(
        self,
        payload: BotXAPISearchUserByOtherIdRequestPayload,
    ) -> BotXAPISearchUserResponsePayload:
        path = "/api/v3/botx/users/by_other_id"

        response = await self._botx_method_call(
            "GET",
            self._build_url(path),
            params=payload.jsonable_dict(),
        )

        return self._verify_and_extract_api_model(
            BotXAPISearchUserResponsePayload,
            response,
        )
