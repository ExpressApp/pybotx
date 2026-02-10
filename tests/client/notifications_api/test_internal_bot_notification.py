import asyncio
from http import HTTPStatus
from typing import Any
from collections.abc import Sequence
from uuid import UUID

import pytest
from respx.router import MockRouter

from pybotx import (
    build_bot,
    BotIsNotChatMemberError,
    ChatNotFoundError,
    FinalRecipientsListEmptyError,
    RateLimitReachedError,
)
from pybotx.presentation.raw_handlers import set_raw_botx_method_result

from pybotx.testkit import BotXRequest, error_payload, mock_botx, ok_payload

pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.mock_authorization,
    pytest.mark.usefixtures("respx_mock"),
]

ENDPOINT = "/api/v4/botx/notifications/internal"

REQUEST = BotXRequest(
    method="POST",
    path=ENDPOINT,
    json={
        "group_chat_id": "054af49e-5e18-4dca-ad73-4f96b6de63fa",
        "data": {"foo": "bar"},
    },
)


async def test__send_internal_bot_notification__rate_limit_reached_error_raised(
    respx_mock: MockRouter,
    host: str,
    bot_id: UUID,
    bot_factory: Any,
) -> None:
    # - Arrange -
    endpoint = mock_botx(
        respx_mock,
        host,
        REQUEST,
        error_payload(
            "too_many_requests",
            error_data={
                "bot_id": "b165f00f-3154-412c-7f11-c120164257da",
            },
        ),
        HTTPStatus.TOO_MANY_REQUESTS,
    )

    # - Act -
    async with bot_factory() as bot:
        with pytest.raises(RateLimitReachedError) as exc:
            await bot.send_internal_bot_notification(
                bot_id=bot_id,
                chat_id=UUID("054af49e-5e18-4dca-ad73-4f96b6de63fa"),
                data={"foo": "bar"},
            )

    # - Assert -
    assert "too_many_requests" in str(exc.value)
    assert endpoint.called


@pytest.mark.parametrize(
    ("reason", "error_data", "expected_exc", "expected_fragments"),
    [
        (
            "chat_not_found",
            {
                "group_chat_id": "21a9ec9e-f21f-4406-ac44-1a78d2ccf9e3",
                "error_description": (
                    "Chat with id 21a9ec9e-f21f-4406-ac44-1a78d2ccf9e3 not found"
                ),
            },
            ChatNotFoundError,
            ("chat_not_found",),
        ),
        (
            "bot_is_not_a_chat_member",
            {
                "group_chat_id": "054af49e-5e18-4dca-ad73-4f96b6de63fa",
                "bot_id": "00000000-0000-0000-0000-000000000000",
                "error_description": "Bot is not a chat member",
            },
            BotIsNotChatMemberError,
            ("bot_is_not_a_chat_member",),
        ),
        (
            "event_recipients_list_is_empty",
            {
                "group_chat_id": "054af49e-5e18-4dca-ad73-4f96b6de63fa",
                "bot_id": "00000000-0000-0000-0000-000000000000",
                "recipients_param": ["b165f00f-3154-412c-7f11-c120164257da"],
                "error_description": "Event recipients list is empty",
            },
            FinalRecipientsListEmptyError,
            ("event_recipients_list_is_empty",),
        ),
    ],
)
async def test__send_internal_bot_notification__callback_error_raised(
    reason: str,
    error_data: dict[str, Any],
    expected_exc: type[Exception],
    expected_fragments: Sequence[str],
    respx_mock: MockRouter,
    host: str,
    bot_id: UUID,
    bot_factory: Any,
) -> None:
    # - Arrange -
    endpoint = mock_botx(
        respx_mock,
        host,
        REQUEST,
        ok_payload({"sync_id": "21a9ec9e-f21f-4406-ac44-1a78d2ccf9e3"}),
        HTTPStatus.ACCEPTED,
    )

    # - Act -
    async with bot_factory() as bot:
        task = asyncio.create_task(
            bot.send_internal_bot_notification(
                bot_id=bot_id,
                chat_id=UUID("054af49e-5e18-4dca-ad73-4f96b6de63fa"),
                data={"foo": "bar"},
            ),
        )
        await asyncio.sleep(0)  # Return control to event loop

        await set_raw_botx_method_result(bot, 
            {
                "status": "error",
                "sync_id": "21a9ec9e-f21f-4406-ac44-1a78d2ccf9e3",
                "reason": reason,
                "errors": [],
                "error_data": error_data,
            },
            verify_request=False,
        )

    # - Assert -
    with pytest.raises(expected_exc) as exc:
        await task

    for fragment in expected_fragments:
        assert fragment in str(exc.value)
    assert endpoint.called


async def test__send_internal_bot_notification__succeed(
    respx_mock: MockRouter,
    host: str,
    bot_id: UUID,
    bot_factory: Any,
) -> None:
    # - Arrange -
    endpoint = mock_botx(
        respx_mock,
        host,
        REQUEST,
        ok_payload({"sync_id": "21a9ec9e-f21f-4406-ac44-1a78d2ccf9e3"}),
        HTTPStatus.ACCEPTED,
    )

    # - Act -
    async with bot_factory() as bot:
        task = asyncio.create_task(
            bot.send_internal_bot_notification(
                bot_id=bot_id,
                chat_id=UUID("054af49e-5e18-4dca-ad73-4f96b6de63fa"),
                data={"foo": "bar"},
            ),
        )
        await asyncio.sleep(0)  # Return control to event loop

        await set_raw_botx_method_result(bot, 
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
