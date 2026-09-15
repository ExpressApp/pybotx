from http import HTTPStatus
from uuid import UUID

import httpx
import pytest
from respx.router import MockRouter

from pybotx import BotAccountWithSecret, BotXAuthVersion, InvalidBotAccountError
from pybotx.bot.bot_accounts_storage import BotAccountsStorage
from tests.client.test_authorized_botx_method import FooBarMethod
from tests.client.test_botx_method import BotXAPIFooBarRequestPayload

pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.usefixtures("respx_mock"),
]


async def test__authorized_botx_method__unauthorized(
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

    foo_bar_endpoint = respx_mock.post(
        f"https://{host}/foo/bar",
        json={"baz": 1},
        headers={"Authorization": "Bearer token", "Content-Type": "application/json"},
    ).mock(
        return_value=httpx.Response(HTTPStatus.UNAUTHORIZED),
    )

    method = FooBarMethod(
        bot_id,
        httpx_client,
        BotAccountsStorage([bot_account], auth_version=BotXAuthVersion.V1),
    )
    payload = BotXAPIFooBarRequestPayload.from_domain(baz=1)

    # - Act -
    with pytest.warns(DeprecationWarning):
        with pytest.raises(InvalidBotAccountError) as exc:
            await method.execute(payload)

    # - Assert -
    assert "failed with code 401" in str(exc.value)
    assert token_endpoint.called
    assert foo_bar_endpoint.called


async def test__authorized_botx_method__succeed(
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

    foo_bar_endpoint = respx_mock.post(
        f"https://{host}/foo/bar",
        json={"baz": 1},
        headers={"Authorization": "Bearer token", "Content-Type": "application/json"},
    ).mock(
        return_value=httpx.Response(
            HTTPStatus.OK,
            json={
                "status": "ok",
                "result": {"sync_id": "21a9ec9e-f21f-4406-ac44-1a78d2ccf9e3"},
            },
        ),
    )

    method = FooBarMethod(
        bot_id,
        httpx_client,
        BotAccountsStorage([bot_account], auth_version=BotXAuthVersion.V1),
    )
    payload = BotXAPIFooBarRequestPayload.from_domain(baz=1)

    # - Act -
    with pytest.warns(DeprecationWarning):
        botx_api_foo_bar = await method.execute(payload)

    # - Assert -
    assert botx_api_foo_bar.to_domain() == UUID("21a9ec9e-f21f-4406-ac44-1a78d2ccf9e3")
    assert token_endpoint.called
    assert foo_bar_endpoint.called


async def test__authorized_botx_method__with_prepared_token(
    httpx_client: httpx.AsyncClient,
    respx_mock: MockRouter,
    host: str,
    bot_id: UUID,
    prepared_bot_accounts_storage: BotAccountsStorage,
) -> None:
    # - Arrange -
    endpoint = respx_mock.post(
        f"https://{host}/foo/bar",
        json={"baz": 1},
        headers={"Authorization": "Bearer token", "Content-Type": "application/json"},
    ).mock(
        return_value=httpx.Response(
            HTTPStatus.OK,
            json={
                "status": "ok",
                "result": {"sync_id": "21a9ec9e-f21f-4406-ac44-1a78d2ccf9e3"},
            },
        ),
    )

    method = FooBarMethod(
        bot_id,
        httpx_client,
        prepared_bot_accounts_storage,
    )

    payload = BotXAPIFooBarRequestPayload.from_domain(baz=1)

    # - Act -
    with pytest.warns(DeprecationWarning):
        botx_api_foo_bar = await method.execute(payload)

    # - Assert -
    assert botx_api_foo_bar.to_domain() == UUID("21a9ec9e-f21f-4406-ac44-1a78d2ccf9e3")
    assert endpoint.called


async def test__authorized_botx_method__legacy_warning_suppressed(
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

    foo_bar_endpoint = respx_mock.post(
        f"https://{host}/foo/bar",
        json={"baz": 1},
        headers={"Authorization": "Bearer token", "Content-Type": "application/json"},
    ).mock(
        return_value=httpx.Response(
            HTTPStatus.OK,
            json={
                "status": "ok",
                "result": {"sync_id": "21a9ec9e-f21f-4406-ac44-1a78d2ccf9e3"},
            },
        ),
    )

    method = FooBarMethod(
        bot_id,
        httpx_client,
        BotAccountsStorage([bot_account], auth_version=BotXAuthVersion.V1),
    )
    method._legacy_auth_warned = True

    payload = BotXAPIFooBarRequestPayload.from_domain(baz=1)

    # - Act -
    botx_api_foo_bar = await method.execute(payload)

    # - Assert -
    assert botx_api_foo_bar.to_domain() == UUID("21a9ec9e-f21f-4406-ac44-1a78d2ccf9e3")
    assert token_endpoint.called
    assert foo_bar_endpoint.called
