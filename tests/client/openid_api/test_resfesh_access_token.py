from http import HTTPStatus
from uuid import UUID

import httpx
import pytest
from respx.router import MockRouter

from pybotx import Bot, BotAccountWithSecret, HandlerCollector, lifespan_wrapper

pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.mock_authorization,
    pytest.mark.usefixtures("respx_mock"),
]


async def test__refresh_access_token__succeed(
    respx_mock: MockRouter,
    host: str,
    bot_id: UUID,
    bot_account: BotAccountWithSecret,
) -> None:
    # - Arrange -
    endpoint = respx_mock.post(
        f"https://{host}/api/v3/botx/openid/refresh_access_token",
        headers={"Authorization": "Bearer token", "Content-Type": "application/json"},
        json={
            "user_huid": "a465f0f3-1354-491c-8f11-f400164295cb",
            "ref": "a465f0f3-1354-491c-8f11-f400164295cb",
        },
    ).mock(
        return_value=httpx.Response(
            HTTPStatus.ACCEPTED,
            json={
                "status": "ok",
                "result": True,
            },
        ),
    )

    built_bot = Bot(collectors=[HandlerCollector()], bot_accounts=[bot_account])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        await bot.refresh_access_token(
            bot_id=bot_id,
            huid=UUID("a465f0f3-1354-491c-8f11-f400164295cb"),
            ref=UUID("a465f0f3-1354-491c-8f11-f400164295cb"),
        )

    # - Assert -
    assert endpoint.called
