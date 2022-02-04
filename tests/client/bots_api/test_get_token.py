from http import HTTPStatus
from uuid import UUID

import httpx
import pytest
from respx.router import MockRouter

from botx import (
    Bot,
    BotAccountWithSecret,
    HandlerCollector,
    InvalidBotAccountError,
    lifespan_wrapper,
)

pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.usefixtures("respx_mock"),
]


async def test__get_token__invalid_bot_account_error_raised(
    respx_mock: MockRouter,
    host: str,
    bot_id: UUID,
    bot_signature: str,
    bot_account: BotAccountWithSecret,
) -> None:
    # - Arrange -
    endpoint = respx_mock.get(
        f"https://{host}/api/v2/botx/bots/{bot_id}/token",
        params={"signature": bot_signature},
    ).mock(
        return_value=httpx.Response(HTTPStatus.UNAUTHORIZED),
    )

    built_bot = Bot(collectors=[HandlerCollector()], bot_accounts=[bot_account])

    # - Act -
    with pytest.raises(InvalidBotAccountError) as exc:
        async with lifespan_wrapper(built_bot) as bot:
            await bot.get_token(bot_id=bot_id)

    # - Assert -
    assert "failed with code 401" in str(exc.value)
    assert endpoint.called


async def test__get_token__succeed(
    respx_mock: MockRouter,
    host: str,
    bot_id: UUID,
    bot_signature: str,
    bot_account: BotAccountWithSecret,
) -> None:
    # - Arrange -
    endpoint = respx_mock.get(
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

    built_bot = Bot(collectors=[HandlerCollector()], bot_accounts=[bot_account])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        token = await bot.get_token(bot_id=bot_id)

    # - Assert -
    assert token == "token"
    assert endpoint.called
