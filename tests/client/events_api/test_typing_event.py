from http import HTTPStatus
from uuid import UUID

import httpx
import pytest
import respx

from botx import Bot, BotAccountWithSecret, HandlerCollector, lifespan_wrapper


@respx.mock
@pytest.mark.asyncio
@pytest.mark.mock_authorization
async def test__start_typing__succeed(
    httpx_client: httpx.AsyncClient,
    host: str,
    bot_id: UUID,
    bot_account: BotAccountWithSecret,
) -> None:
    # - Arrange -
    endpoint = respx.post(
        f"https://{host}/api/v3/botx/events/typing",
        headers={"Authorization": "Bearer token", "Content-Type": "application/json"},
        json={
            "group_chat_id": "054af49e-5e18-4dca-ad73-4f96b6de63fa",
        },
    ).mock(
        return_value=httpx.Response(
            HTTPStatus.OK,
            json={"status": "ok", "result": "typing_event_pushed"},
        ),
    )

    built_bot = Bot(
        collectors=[HandlerCollector()],
        bot_accounts=[bot_account],
        httpx_client=httpx_client,
    )

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        await bot.start_typing(
            bot_id=bot_id,
            chat_id=UUID("054af49e-5e18-4dca-ad73-4f96b6de63fa"),
        )

    # - Assert -
    assert endpoint.called
