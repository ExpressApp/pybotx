from http import HTTPStatus
from uuid import UUID

import httpx
import pytest
from respx import MockRouter

from pybotx import Bot, BotAccountWithSecret, HandlerCollector, lifespan_wrapper

pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.mock_authorization,
    pytest.mark.usefixtures("respx_mock"),
]


async def test__collect_bot_function_metric__success(
    respx_mock: MockRouter,
    host: str,
    bot_id: UUID,
    bot_account: BotAccountWithSecret,
) -> None:
    # - Arrange -
    endpoint = respx_mock.post(
        f"https://{host}/api/v3/botx/metrics/bot_function",
        headers={"Authorization": "Bearer token", "Content-Type": "application/json"},
        json={
            "user_huids": ["33bd8924-da34-4615-b8ea-f8f7139bf4ef"],
            "group_chat_id": "3c11c28e-fbe1-4080-86e8-58e03c217dae",
            "bot_function": "email_sent",
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
        await bot.collect_metric(
            bot_id=bot_id,
            bot_function="email_sent",
            huids=[UUID("33bd8924-da34-4615-b8ea-f8f7139bf4ef")],
            chat_id=UUID("3c11c28e-fbe1-4080-86e8-58e03c217dae"),
        )

    # - Assert -
    assert endpoint.called
