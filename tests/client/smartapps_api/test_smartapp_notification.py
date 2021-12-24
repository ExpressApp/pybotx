from http import HTTPStatus
from uuid import UUID

import httpx
import pytest
import respx

from botx import Bot, BotAccountWithSecret, HandlerCollector, lifespan_wrapper


@respx.mock
@pytest.mark.asyncio
@pytest.mark.mock_authorization
async def test__send_smartapp_notification__succeed(
    httpx_client: httpx.AsyncClient,
    host: str,
    bot_id: UUID,
    bot_account: BotAccountWithSecret,
) -> None:
    # - Arrange -
    endpoint = respx.post(
        f"https://{host}/api/v3/botx/smartapps/notification",
        headers={"Authorization": "Bearer token", "Content-Type": "application/json"},
        json={
            "group_chat_id": "705df263-6bfd-536a-9d51-13524afaab5c",
            "smartapp_counter": 42,
            "opts": {"message": "ping"},
            "smartapp_api_version": 1,
        },
    ).mock(
        return_value=httpx.Response(
            HTTPStatus.ACCEPTED,
            json={
                "status": "ok",
                "result": "smartapp_notification_pushed",
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
        await bot.send_smartapp_notification(
            bot_id=bot_id,
            chat_id=UUID("705df263-6bfd-536a-9d51-13524afaab5c"),
            smartapp_counter=42,
            opts={"message": "ping"},
        )

    # - Assert -
    assert endpoint.called
