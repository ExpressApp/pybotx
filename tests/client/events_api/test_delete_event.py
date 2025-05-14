from http import HTTPStatus
from uuid import UUID

import httpx
import pytest
from respx.router import MockRouter

from pybotx import (
    Bot,
    BotAccountWithSecret,
    HandlerCollector,
    MessageNotFoundError,
    lifespan_wrapper,
)

pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.mock_authorization,
    pytest.mark.usefixtures("respx_mock"),
]


async def test__delete_message__succeed(
    respx_mock: MockRouter,
    host: str,
    bot_id: UUID,
    bot_account: BotAccountWithSecret,
) -> None:
    # - Arrange -
    endpoint = respx_mock.post(
        f"https://{host}/api/v3/botx/events/delete_event",
        headers={"Authorization": "Bearer token", "Content-Type": "application/json"},
        json={
            "sync_id": "8ba66c5b-40bf-5c77-911d-519cb4e382e9",
        },
    ).mock(
        return_value=httpx.Response(
            HTTPStatus.ACCEPTED,
            json={
                "status": "ok",
                "result": "event_deleted",
            },
        ),
    )

    built_bot = Bot(collectors=[HandlerCollector()], bot_accounts=[bot_account])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        await bot.delete_message(
            bot_id=bot_id,
            sync_id=UUID("8ba66c5b-40bf-5c77-911d-519cb4e382e9"),
        )

    # - Assert -
    assert endpoint.called


async def test__delete_message__message_not_found_error_raised(
    respx_mock: MockRouter,
    host: str,
    bot_id: UUID,
    bot_account: BotAccountWithSecret,
) -> None:
    # - Arrange -
    endpoint = respx_mock.post(
        f"https://{host}/api/v3/botx/events/delete_event",
        headers={"Authorization": "Bearer token", "Content-Type": "application/json"},
        json={
            "sync_id": "fe1f285c-073e-4231-b190-2959f28168cc",
        },
    ).mock(
        return_value=httpx.Response(
            HTTPStatus.NOT_FOUND,
            json={
                "status": "error",
                "reason": "sync_id_not_found",
                "errors": [],
                "error_data": {},
            },
        ),
    )

    built_bot = Bot(collectors=[HandlerCollector()], bot_accounts=[bot_account])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        with pytest.raises(MessageNotFoundError) as exc:
            await bot.delete_message(
                bot_id=bot_id,
                sync_id=UUID("fe1f285c-073e-4231-b190-2959f28168cc"),
            )

    # - Assert -
    assert "sync_id_not_found" in str(exc.value)
    assert endpoint.called
