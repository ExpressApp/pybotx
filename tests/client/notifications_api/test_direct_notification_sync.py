from http import HTTPStatus
from typing import Type
from uuid import UUID

import httpx
import pytest
from respx.router import MockRouter

from pybotx import (
    Bot,
    BotAccountWithSecret,
    BotIsNotChatMemberError,
    ChatNotFoundError,
    FinalRecipientsListEmptyError,
    HandlerCollector,
    StealthModeDisabledError,
    lifespan_wrapper,
)
from pybotx.client.exceptions.http import InvalidBotXResponsePayloadError

pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.mock_authorization,
    pytest.mark.usefixtures("respx_mock"),
]


async def test__send_message_sync__succeed(
    respx_mock: MockRouter,
    host: str,
    bot_account: BotAccountWithSecret,
    bot_id: UUID,
) -> None:
    # - Arrange -
    endpoint = respx_mock.post(
        f"https://{host}/api/v4/botx/notifications/direct/sync",
        headers={"Authorization": "Bearer token", "Content-Type": "application/json"},
        json={
            "group_chat_id": "054af49e-5e18-4dca-ad73-4f96b6de63fa",
            "notification": {"status": "ok", "body": "Hi!"},
        },
    ).mock(
        return_value=httpx.Response(
            HTTPStatus.OK,
            json={
                "status": "ok",
                "result": {"sync_id": "21a9ec9e-f21f-4406-ac44-1a78d2ccf9e3"},
            },
        ),
    )

    built_bot = Bot(collectors=[HandlerCollector()], bot_accounts=[bot_account])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        sync_id = await bot.send_message_sync(
            body="Hi!",
            bot_id=bot_id,
            chat_id=UUID("054af49e-5e18-4dca-ad73-4f96b6de63fa"),
        )

    # - Assert -
    assert sync_id == UUID("21a9ec9e-f21f-4406-ac44-1a78d2ccf9e3")
    assert endpoint.called


@pytest.mark.parametrize(
    ("reason", "exc_type"),
    [
        ("chat_not_found", ChatNotFoundError),
        ("bot_is_not_a_chat_member", BotIsNotChatMemberError),
        ("event_recipients_list_is_empty", FinalRecipientsListEmptyError),
        ("stealth_mode_disabled", StealthModeDisabledError),
    ],
)
async def test__send_message_sync__known_error_reason_raised(
    reason: str,
    exc_type: Type[Exception],
    respx_mock: MockRouter,
    host: str,
    bot_account: BotAccountWithSecret,
    bot_id: UUID,
) -> None:
    # - Arrange -
    endpoint = respx_mock.post(
        f"https://{host}/api/v4/botx/notifications/direct/sync",
        headers={"Authorization": "Bearer token", "Content-Type": "application/json"},
        json={
            "group_chat_id": "054af49e-5e18-4dca-ad73-4f96b6de63fa",
            "notification": {"status": "ok", "body": "Hi!"},
        },
    ).mock(
        return_value=httpx.Response(
            HTTPStatus.OK,
            json={
                "status": "error",
                "reason": reason,
                "errors": [],
                "error_data": {
                    "group_chat_id": "054af49e-5e18-4dca-ad73-4f96b6de63fa",
                },
            },
        ),
    )

    built_bot = Bot(collectors=[HandlerCollector()], bot_accounts=[bot_account])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        with pytest.raises(exc_type):
            await bot.send_message_sync(
                body="Hi!",
                bot_id=bot_id,
                chat_id=UUID("054af49e-5e18-4dca-ad73-4f96b6de63fa"),
            )

    # - Assert -
    assert endpoint.called


async def test__send_message_sync__unknown_error_reason_raised(
    respx_mock: MockRouter,
    host: str,
    bot_account: BotAccountWithSecret,
    bot_id: UUID,
) -> None:
    # - Arrange -
    endpoint = respx_mock.post(
        f"https://{host}/api/v4/botx/notifications/direct/sync",
        headers={"Authorization": "Bearer token", "Content-Type": "application/json"},
        json={
            "group_chat_id": "054af49e-5e18-4dca-ad73-4f96b6de63fa",
            "notification": {"status": "ok", "body": "Hi!"},
        },
    ).mock(
        return_value=httpx.Response(
            HTTPStatus.OK,
            json={
                "status": "error",
                "reason": "unknown_reason",
                "errors": [],
                "error_data": {},
            },
        ),
    )

    built_bot = Bot(collectors=[HandlerCollector()], bot_accounts=[bot_account])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        with pytest.raises(InvalidBotXResponsePayloadError):
            await bot.send_message_sync(
                body="Hi!",
                bot_id=bot_id,
                chat_id=UUID("054af49e-5e18-4dca-ad73-4f96b6de63fa"),
            )

    # - Assert -
    assert endpoint.called
