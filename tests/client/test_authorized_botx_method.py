from http import HTTPStatus
from uuid import UUID

import httpx
import pytest
import respx

from botx import BotAccount
from botx.bot.bot_accounts_storage import BotAccountsStorage
from botx.client.authorized_botx_method import AuthorizedBotXMethod
from tests.client.test_botx_method import BotXAPIFooBar, BotXAPIFooBarPayload


class FooBarMethod(AuthorizedBotXMethod):
    async def execute(self, payload: BotXAPIFooBarPayload) -> BotXAPIFooBar:
        path = "/foo/bar"

        response = await self._botx_method_call(
            "GET",
            self._build_url(path),
            params=payload.jsonable_dict(),
        )

        return self._extract_api_model(BotXAPIFooBar, response)


@respx.mock
@pytest.mark.asyncio
async def test__authorized_botx_method__succeed(
    httpx_client: httpx.AsyncClient,
    host: str,
    bot_id: UUID,
    bot_signature: str,
    bot_account: BotAccount,
) -> None:
    # - Arrange -
    token_endpoint = respx.get(
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

    foo_bar_endpoint = respx.get(
        f"https://{host}/foo/bar",
        params={"baz": 1},
        headers={"Authorization": "Bearer token", "Content-Type": "application/json"},
    ).mock(
        return_value=httpx.Response(
            HTTPStatus.OK,
            json={
                "quux": 3,
            },
        ),
    )

    method = FooBarMethod(
        bot_id,
        httpx_client,
        BotAccountsStorage([bot_account]),
    )
    payload = BotXAPIFooBarPayload.from_domain(baz=1)

    # - Act -
    botx_api_foo_bar = await method.execute(payload)

    # - Assert -
    assert botx_api_foo_bar.to_domain() == 3
    assert token_endpoint.called
    assert foo_bar_endpoint.called


@respx.mock
@pytest.mark.asyncio
async def test__authorized_botx_method__with_prepared_token(
    httpx_client: httpx.AsyncClient,
    host: str,
    bot_id: UUID,
    bot_signature: str,
    bot_account: BotAccount,
    prepared_bot_accounts_storage: BotAccountsStorage,
) -> None:
    # - Arrange -
    endpoint = respx.get(
        f"https://{host}/foo/bar",
        params={"baz": 1},
        headers={"Authorization": "Bearer token", "Content-Type": "application/json"},
    ).mock(
        return_value=httpx.Response(
            HTTPStatus.OK,
            json={
                "quux": 3,
            },
        ),
    )

    method = FooBarMethod(
        bot_id,
        httpx_client,
        prepared_bot_accounts_storage,
    )

    payload = BotXAPIFooBarPayload.from_domain(baz=1)

    # - Act -
    botx_api_foo_bar = await method.execute(payload)

    # - Assert -
    assert botx_api_foo_bar.to_domain() == 3
    assert endpoint.called
