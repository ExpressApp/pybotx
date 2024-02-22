import asyncio
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


async def test__send_smartapp_custom_notification__succeed(
    respx_mock: MockRouter,
    host: str,
    bot_id: UUID,
    bot_account: BotAccountWithSecret,
) -> None:
    # - Arrange -
    endpoint = respx_mock.post(
        f"https://{host}/api/v4/botx/smartapps/notification",
        headers={"Authorization": "Bearer token", "Content-Type": "application/json"},
        json={
            "group_chat_id": "705df263-6bfd-536a-9d51-13524afaab5c",
            "payload": {
                "title": "test",
                "body": "test",
            },
            "meta": {"message": "ping"},
        },
    ).mock(
        return_value=httpx.Response(
            HTTPStatus.ACCEPTED,
            json={
                "status": "ok",
                "result": {"sync_id": "21a9ec9e-f21f-4406-ac44-1a78d2ccf9e3"},
            },
        ),
    )

    built_bot = Bot(collectors=[HandlerCollector()], bot_accounts=[bot_account])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        task = asyncio.create_task(
            bot.send_smartapp_custom_notification(
                bot_id=bot_id,
                group_chat_id=UUID("705df263-6bfd-536a-9d51-13524afaab5c"),
                title="test",
                body="test",
                meta={"message": "ping"},
            ),
        )
        await asyncio.sleep(0)  # Return control to event loop

        await bot.set_raw_botx_method_result(
            {
                "status": "ok",
                "sync_id": "21a9ec9e-f21f-4406-ac44-1a78d2ccf9e3",
                "result": {},
            },
            verify_request=False,
        )

    # - Assert -
    assert await task == UUID("21a9ec9e-f21f-4406-ac44-1a78d2ccf9e3")
    assert endpoint.called
