from http import HTTPStatus
from uuid import UUID

import httpx
import pytest
import respx

from botx import (
    Bot,
    BotCredentials,
    HandlerCollector,
    InvalidBotCredentialsError,
    lifespan_wrapper,
)


@respx.mock
@pytest.mark.asyncio
async def test_invalid_credentials(
    httpx_client: httpx.AsyncClient,
    host: str,
    bot_id: UUID,
    bot_signature: str,
    bot_credentials: BotCredentials,
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
        credentials=[bot_credentials],
        httpx_client=httpx_client,
    )

    # - Act -
    with pytest.raises(InvalidBotCredentialsError) as exc:
        async with lifespan_wrapper(built_bot) as bot:
            await bot.get_token(bot_id)

    # - Assert -
    assert "failed with code 401" in str(exc)
    assert endpoint.called


@respx.mock
@pytest.mark.asyncio
async def test_get_token(
    httpx_client: httpx.AsyncClient,
    host: str,
    bot_id: UUID,
    bot_signature: str,
    bot_credentials: BotCredentials,
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
        credentials=[bot_credentials],
        httpx_client=httpx_client,
    )

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        token = await bot.get_token(bot_id)

    # - Assert -
    assert token == "token"
    assert endpoint.called
