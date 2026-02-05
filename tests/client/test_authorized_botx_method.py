from http import HTTPStatus
from uuid import UUID

import httpx
import jwt
import pytest
from respx.router import MockRouter

from pybotx import BotAccountWithSecret, BotXAuthVersion
from pybotx.bot.bot_accounts_storage import BotAccountsStorage
from pybotx.client.authorized_botx_method import AuthorizedBotXMethod
from tests.client.test_botx_method import (
    BotXAPIFooBarRequestPayload,
    BotXAPIFooBarResponsePayload,
)


class FooBarMethod(AuthorizedBotXMethod):
    async def execute(
        self,
        payload: BotXAPIFooBarRequestPayload,
    ) -> BotXAPIFooBarResponsePayload:
        path = "/foo/bar"

        response = await self._botx_method_call(
            "POST",
            self._build_url(path),
            json=payload.jsonable_dict(),
        )

        return self._verify_and_extract_api_model(
            BotXAPIFooBarResponsePayload,
            response,
        )


pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.usefixtures("respx_mock"),
]


async def test__authorized_botx_method__v2_succeed(
    httpx_client: httpx.AsyncClient,
    respx_mock: MockRouter,
    host: str,
    bot_id: UUID,
    bot_signature: str,
    bot_account: BotAccountWithSecret,
) -> None:
    # - Arrange -
    token_endpoint = respx_mock.get(
        f"https://{host}/api/v2/botx/bots/{bot_id}/token",
        params={"signature": bot_signature},
    ).mock(
        return_value=httpx.Response(
            HTTPStatus.OK,
            json={
                "status": "ok",
                "result": "token",
            },
        ),
    )

    def responder(request: httpx.Request) -> httpx.Response:
        authorization = request.headers.get("Authorization")
        assert authorization is not None
        token = authorization.split()[-1]
        payload = jwt.decode(
            jwt=token,
            key=bot_account.secret_key,
            algorithms=["HS256"],
            options={"verify_aud": False, "verify_iss": False},
        )
        assert payload["iss"] == str(bot_id)
        assert payload["aud"] == host
        assert payload["version"] == 2
        assert payload["exp"] - payload["iat"] == 60
        assert payload["nbf"] == payload["iat"]
        return httpx.Response(
            HTTPStatus.OK,
            json={
                "status": "ok",
                "result": {"sync_id": "21a9ec9e-f21f-4406-ac44-1a78d2ccf9e3"},
            },
        )

    foo_bar_endpoint = respx_mock.post(
        f"https://{host}/foo/bar",
        json={"baz": 1},
    ).mock(side_effect=responder)

    method = FooBarMethod(
        bot_id,
        httpx_client,
        BotAccountsStorage([bot_account], auth_version=BotXAuthVersion.V2),
    )
    payload = BotXAPIFooBarRequestPayload.from_domain(baz=1)

    # - Act -
    botx_api_foo_bar = await method.execute(payload)

    # - Assert -
    assert botx_api_foo_bar.to_domain() == UUID("21a9ec9e-f21f-4406-ac44-1a78d2ccf9e3")
    assert foo_bar_endpoint.called
    assert not token_endpoint.called
