from http import HTTPStatus
from uuid import UUID

import httpx
import pytest
from respx.router import MockRouter

from pybotx import (
    Bot,
    BotAccountWithSecret,
    HandlerCollector,
    lifespan_wrapper,
)
from pybotx.client.voex_api.exceptions import CallNotFoundError
from pybotx.models.call import Call

pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.mock_authorization,
    pytest.mark.usefixtures("respx_mock"),
]


async def test__get_call__succeed(
    respx_mock: MockRouter,
    host: str,
    bot_id: UUID,
    bot_account: BotAccountWithSecret,
) -> None:
    # - Arrange -
    call_id = "a465f0f3-1354-491c-8f11-f400164295cb"
    member1 = "dcfa5a7c-7cc4-4c89-b6c0-80325604f9f4"
    member2 = "6fa5f1e9-1453-0ad7-2d6d-b791467e382a"

    endpoint = respx_mock.get(
        f"https://{host}/api/v3/botx/voex/calls/{call_id}",
        headers={"Authorization": "Bearer token"},
    ).mock(
        return_value=httpx.Response(
            HTTPStatus.OK,
            json={
                "status": "ok",
                "result": {
                    "id": call_id,
                    "members": [
                        member1,
                        member2,
                    ],
                },
            },
        ),
    )

    built_bot = Bot(collectors=[HandlerCollector()], bot_accounts=[bot_account])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        call = await bot.get_call(
            bot_id=bot_id,
            call_id=UUID(call_id),
        )

    # - Assert -
    assert call == Call(
        id=UUID(call_id),
        members=[
            UUID(member1),
            UUID(member2),
        ],
    )

    assert endpoint.called


async def test__get_call__call_not_found(
    respx_mock: MockRouter,
    host: str,
    bot_id: UUID,
    bot_account: BotAccountWithSecret,
) -> None:
    # - Arrange -
    call_id = "a465f0f3-1354-491c-8f11-f400164295cb"

    endpoint = respx_mock.get(
        f"https://{host}/api/v3/botx/voex/calls/{call_id}",
        headers={"Authorization": "Bearer token"},
    ).mock(
        return_value=httpx.Response(
            HTTPStatus.NOT_FOUND,
            json={
                "error_data": {
                    "call_id": call_id,
                },
                "errors": ["Call with specified call_id not found."],
                "reason": "not_found",
                "status": "error",
            },
        ),
    )

    built_bot = Bot(collectors=[HandlerCollector()], bot_accounts=[bot_account])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        with pytest.raises(CallNotFoundError) as exc:
            await bot.get_call(
                bot_id=bot_id,
                call_id=UUID(call_id),
            )

    # - Assert -
    assert "not_found" in str(exc.value)
    assert endpoint.called
