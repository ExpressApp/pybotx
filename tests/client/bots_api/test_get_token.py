from http import HTTPStatus
from uuid import UUID

import httpx
import pytest
import respx

from botx import (
    Bot,
    BotAccountWithSecret,
    HandlerCollector,
    InvalidBotAccountError,
    lifespan_wrapper,
)


@respx.mock
@pytest.mark.asyncio
async def test__get_token__invalid_bot_account_error_raised(
    httpx_client: httpx.AsyncClient,
    host: str,
    bot_id: UUID,
    bot_signature: str,
    bot_account: BotAccountWithSecret,
) -> None:
    # - Arrange -
    endpoint = respx.get(
        f"https://{host}/api/v2/botx/bots/{bot_id}/token",
        params={"signature": bot_signature},
    ).mock(
        return_value=httpx.Response(HTTPStatus.UNAUTHORIZED),
    )

    built_bot = Bot(
        collectors=[HandlerCollector()],
        bot_accounts=[bot_account],
        httpx_client=httpx_client,
    )

    # - Act -
    with pytest.raises(InvalidBotAccountError) as exc:
        async with lifespan_wrapper(built_bot) as bot:
            await bot.get_token(bot_id=bot_id)

    # - Assert -
    assert "failed with code 401" in str(exc.value)
    assert endpoint.called


@respx.mock
@pytest.mark.asyncio
async def test__get_token__succeed(
    httpx_client: httpx.AsyncClient,
    host: str,
    bot_id: UUID,
    bot_signature: str,
    bot_account: BotAccountWithSecret,
) -> None:
    # - Arrange -
    endpoint = respx.get(
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

    built_bot = Bot(
        collectors=[HandlerCollector()],
        bot_accounts=[bot_account],
        httpx_client=httpx_client,
    )

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        token = await bot.get_token(bot_id=bot_id)

    # - Assert -
    assert token == "token"
    assert endpoint.called
