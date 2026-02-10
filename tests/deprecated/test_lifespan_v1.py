from http import HTTPStatus
from uuid import UUID

import httpx
import pytest
from respx.router import MockRouter

from pybotx import Bot, BotAccountWithSecret, BotXAuthVersion, HandlerCollector
from pybotx import build_bot

pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.mock_authorization,
    pytest.mark.usefixtures("respx_mock"),
]


async def test__startup__authorize_cant_get_token(
    respx_mock: MockRouter,
    loguru_caplog: pytest.LogCaptureFixture,
    bot_account: BotAccountWithSecret,
    host: str,
    bot_id: UUID,
    bot_signature: str,
) -> None:
    # - Arrange -
    token_endpoint = respx_mock.get(
        f"https://{host}/api/v2/botx/bots/{bot_id}/token",
        params={"signature": bot_signature},
    ).mock(
        return_value=httpx.Response(
            HTTPStatus.UNAUTHORIZED,
            json={
                "status": "error",
            },
        ),
    )

    collector = HandlerCollector()

    bot = build_bot(
        collectors=[collector],
        bot_accounts=[bot_account],
        auth_version=BotXAuthVersion.V1,
    )

    # - Act -
    await bot.startup()

    # - Assert -
    assert token_endpoint.called

    assert "Can't get token for bot account: " in loguru_caplog.text
    assert f"host - {host}, bot_id - {bot_id}" in loguru_caplog.text

    # Cleanup
    await bot.shutdown()


async def test__startup__can_skip_fetching_tokens(
    respx_mock: MockRouter,
    bot_account: BotAccountWithSecret,
    host: str,
    bot_id: UUID,
    bot_signature: str,
) -> None:
    # - Arrange -
    token_endpoint = respx_mock.get(
        f"https://{host}/api/v2/botx/bots/{bot_id}/token",
        params={"signature": bot_signature},
    )

    collector = HandlerCollector()

    bot = build_bot(
        collectors=[collector],
        bot_accounts=[bot_account],
        auth_version=BotXAuthVersion.V1,
    )

    # - Act -
    await bot.startup(fetch_tokens=False)

    # - Assert -
    assert not token_endpoint.called

    # Cleanup
    await bot.shutdown()


async def test__fetch_tokens__succeeds_for_auth_v1(
    respx_mock: MockRouter,
    bot_account: BotAccountWithSecret,
    host: str,
    bot_id: UUID,
    bot_signature: str,
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

    collector = HandlerCollector()
    bot = build_bot(
        collectors=[collector],
        bot_accounts=[bot_account],
        auth_version=BotXAuthVersion.V1,
    )

    # - Act -
    await bot.fetch_tokens()

    # - Assert -
    assert token_endpoint.called
    assert bot._bot_accounts_storage.get_token_or_none(bot_id) == "token"

    # Cleanup
    await bot.shutdown()
