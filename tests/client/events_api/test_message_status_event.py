from datetime import datetime
from http import HTTPStatus
from typing import Callable
from uuid import UUID

import httpx
import pytest
from respx.router import MockRouter

from botx import (
    Bot,
    BotAccountWithSecret,
    EventNotFoundError,
    HandlerCollector,
    MessageStatus,
    lifespan_wrapper,
)

pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.mock_authorization,
    pytest.mark.usefixtures("respx_mock"),
]


async def test__get_message_status__event_not_found_error_raised(
    respx_mock: MockRouter,
    host: str,
    bot_id: UUID,
    bot_account: BotAccountWithSecret,
) -> None:
    # - Arrange -
    endpoint = respx_mock.get(
        f"https://{host}/api/v3/botx/events/fe1f285c-073e-4231-b190-2959f28168cc/status",
        headers={"Authorization": "Bearer token"},
    ).mock(
        return_value=httpx.Response(
            HTTPStatus.NOT_FOUND,
            json={
                "status": "error",
                "reason": "event_not_found",
                "errors": [],
                "error_data": {"sync_id": "fe1f285c-073e-4231-b190-2959f28168cc"},
            },
        ),
    )

    built_bot = Bot(collectors=[HandlerCollector()], bot_accounts=[bot_account])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        with pytest.raises(EventNotFoundError) as exc:
            await bot.get_message_status(
                bot_id=bot_id,
                sync_id=UUID("fe1f285c-073e-4231-b190-2959f28168cc"),
            )

        # - Assert -
        assert "event_not_found" in str(exc.value)
        assert endpoint.called


async def test__get_message_status__succeed(
    respx_mock: MockRouter,
    host: str,
    bot_id: UUID,
    bot_account: BotAccountWithSecret,
    datetime_formatter: Callable[[str], datetime],
) -> None:
    # - Arrange -
    endpoint = respx_mock.get(
        f"https://{host}/api/v3/botx/events/fe1f285c-073e-4231-b190-2959f28168cc/status",
        headers={"Authorization": "Bearer token"},
    ).mock(
        return_value=httpx.Response(
            HTTPStatus.ACCEPTED,
            json={
                "status": "ok",
                "result": {
                    "group_chat_id": "740cf331-d833-5250-b5a5-5b5cbc697ff5",
                    "sent_to": ["32bb051e-cee9-5c5c-9c35-f213ec18d11e"],
                    "read_by": [
                        {
                            "user_huid": "6fafda2c-6505-57a5-a088-25ea5d1d0364",
                            "read_at": "2019-08-29T11:22:48.358586Z",
                        },
                    ],
                    "received_by": [
                        {
                            "user_huid": "6fafda2c-6505-57a5-a088-25ea5d1d0364",
                            "received_at": "2019-08-29T11:22:48.358586Z",
                        },
                    ],
                },
            },
        ),
    )

    built_bot = Bot(collectors=[HandlerCollector()], bot_accounts=[bot_account])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        message_status = await bot.get_message_status(
            bot_id=bot_id,
            sync_id=UUID("fe1f285c-073e-4231-b190-2959f28168cc"),
        )

    # - Assert -
    assert message_status == MessageStatus(
        group_chat_id=UUID("740cf331-d833-5250-b5a5-5b5cbc697ff5"),
        sent_to=[UUID("32bb051e-cee9-5c5c-9c35-f213ec18d11e")],
        read_by={
            UUID("6fafda2c-6505-57a5-a088-25ea5d1d0364"): datetime_formatter(
                "2019-08-29T11:22:48.358586Z",
            ),
        },
        received_by={
            UUID("6fafda2c-6505-57a5-a088-25ea5d1d0364"): datetime_formatter(
                "2019-08-29T11:22:48.358586Z",
            ),
        },
    )
    assert endpoint.called
