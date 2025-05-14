from pybotx.async_buffer import AsyncBufferWritable
from pybotx.client.authorized_botx_method import AuthorizedBotXMethod
from pybotx.client.botx_method import response_exception_thrower
from pybotx.client.exceptions.users import NoUserKindSelectedError
from pybotx.models.api_base import UnverifiedPayloadBaseModel


class BotXAPIUsersAsCSVRequestPayload(UnverifiedPayloadBaseModel):
    cts_user: bool
    unregistered: bool
    botx: bool

    @classmethod
    def from_domain(
        cls,
        cts_user: bool,
        unregistered: bool,
        botx: bool,
    ) -> "BotXAPIUsersAsCSVRequestPayload":
        return cls(
            cts_user=cts_user,
            unregistered=unregistered,
            botx=botx,
        )


class UsersAsCSVMethod(AuthorizedBotXMethod):
    status_handlers = {
        **AuthorizedBotXMethod.status_handlers,
        400: response_exception_thrower(NoUserKindSelectedError),
    }

    async def execute(
        self,
        payload: BotXAPIUsersAsCSVRequestPayload,
        async_buffer: AsyncBufferWritable,
    ) -> None:
        path = "/api/v3/botx/users/users_as_csv"

        async with self._botx_method_stream(
            "GET",
            self._build_url(path),
            params=payload.jsonable_dict(),
        ) as response:
            # https://github.com/nedbat/coveragepy/issues/1223
            async for chunk in response.aiter_bytes():  # pragma: no cover
                await async_buffer.write(chunk)
