import warnings

from pybotx.client.authorized_botx_method import AuthorizedBotXMethod
from pybotx.client.botx_method import response_exception_thrower
from pybotx.client.exceptions.http import InvalidBotXResponsePayloadError
from pybotx.client.exceptions.users import UserNotFoundError
from pybotx.client.users_api.user_from_search import (
    BotXAPISearchUserByEmailsResponsePayload,
    BotXAPISearchUserResponsePayload,
)
from pybotx.logger import logger
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
    _legacy_get_warned: bool = False

    async def execute(
        self,
        payload: BotXAPISearchUserByEmailRequestPayload,
    ) -> BotXAPISearchUserResponsePayload:
        if not type(self)._legacy_get_warned:
            warnings.warn(
                "GET /api/v3/botx/users/by_email is deprecated; "
                "use POST /api/v3/botx/users/by_email instead",
                DeprecationWarning,
                stacklevel=2,
            )
            type(self)._legacy_get_warned = True

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


class SearchUserByEmailPostMethod(AuthorizedBotXMethod):
    status_handlers = {
        **AuthorizedBotXMethod.status_handlers,
        404: response_exception_thrower(UserNotFoundError),
    }

    async def execute(
        self,
        payload: BotXAPISearchUserByEmailRequestPayload,
    ) -> BotXAPISearchUserResponsePayload:
        path = "/api/v3/botx/users/by_email"

        email = payload.email
        request_json = {"emails": [email]}

        response = await self._botx_method_call(
            "POST",
            self._build_url(path),
            json=request_json,
        )

        try:
            list_payload = self._verify_and_extract_api_model(
                BotXAPISearchUserByEmailsResponsePayload,
                response,
            )
        except InvalidBotXResponsePayloadError as exc:
            raise exc

        if not list_payload.result:
            raise UserNotFoundError("User not found")

        if len(list_payload.result) > 1:
            logger.warning(
                "Search by email returned multiple users; taking the first result"
            )

        return BotXAPISearchUserResponsePayload(
            status="ok",
            result=list_payload.result[0],
        )
