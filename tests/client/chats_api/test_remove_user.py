from http import HTTPStatus
from uuid import UUID

import httpx
import pytest
from respx.router import MockRouter

from botx import (
    Bot,
    BotAccountWithSecret,
    ChatNotFoundError,
    HandlerCollector,
    PermissionDeniedError,
    lifespan_wrapper,
)

pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.mock_authorization,
    pytest.mark.usefixtures("respx_mock"),
]


async def test__remove_users_from_chat__permission_denied_error_raised(
    respx_mock: MockRouter,
    host: str,
    bot_id: UUID,
    bot_account: BotAccountWithSecret,
) -> None:
    # - Arrange -
    endpoint = respx_mock.post(
        f"https://{host}/api/v3/botx/chats/remove_user",
        headers={"Authorization": "Bearer token", "Content-Type": "application/json"},
        json={
            "group_chat_id": "054af49e-5e18-4dca-ad73-4f96b6de63fa",
            "user_huids": ["f837dff4-d3ad-4b8d-a0a3-5c6ca9c747d1"],
        },
    ).mock(
        return_value=httpx.Response(
            HTTPStatus.FORBIDDEN,
            json={
                "status": "error",
                "reason": "no_permission_for_operation",
                "errors": ["Sender is not chat admin"],
                "error_data": {
                    "group_chat_id": "dcfa5a7c-7cc4-4c89-b6c0-80325604f9f4",
                    "sender": "a465f0f3-1354-491c-8f11-f400164295cb",
                },
            },
        ),
    )

    built_bot = Bot(collectors=[HandlerCollector()], bot_accounts=[bot_account])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        with pytest.raises(PermissionDeniedError) as exc:
            await bot.remove_users_from_chat(
                bot_id=bot_id,
                chat_id=UUID("054af49e-5e18-4dca-ad73-4f96b6de63fa"),
                huids=[UUID("f837dff4-d3ad-4b8d-a0a3-5c6ca9c747d1")],
            )

    # - Assert -
    assert "no_permission_for_operation" in str(exc.value)
    assert endpoint.called


async def test__remove_users_from_chat__chat_not_found_error_raised(
    respx_mock: MockRouter,
    host: str,
    bot_id: UUID,
    bot_account: BotAccountWithSecret,
) -> None:
    # - Arrange -
    endpoint = respx_mock.post(
        f"https://{host}/api/v3/botx/chats/remove_user",
        headers={"Authorization": "Bearer token", "Content-Type": "application/json"},
        json={
            "group_chat_id": "054af49e-5e18-4dca-ad73-4f96b6de63fa",
            "user_huids": ["f837dff4-d3ad-4b8d-a0a3-5c6ca9c747d1"],
        },
    ).mock(
        return_value=httpx.Response(
            HTTPStatus.NOT_FOUND,
            json={
                "status": "error",
                "reason": "chat_not_found",
                "errors": ["Chat not found"],
                "error_data": {
                    "group_chat_id": "dcfa5a7c-7cc4-4c89-b6c0-80325604f9f4",
                },
            },
        ),
    )

    built_bot = Bot(collectors=[HandlerCollector()], bot_accounts=[bot_account])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        with pytest.raises(ChatNotFoundError) as exc:
            await bot.remove_users_from_chat(
                bot_id=bot_id,
                chat_id=UUID("054af49e-5e18-4dca-ad73-4f96b6de63fa"),
                huids=[UUID("f837dff4-d3ad-4b8d-a0a3-5c6ca9c747d1")],
            )

    # - Assert -
    assert "chat_not_found" in str(exc.value)
    assert endpoint.called


async def test__remove_users_from_chat__succeed(
    respx_mock: MockRouter,
    host: str,
    bot_id: UUID,
    bot_account: BotAccountWithSecret,
) -> None:
    # - Arrange -
    endpoint = respx_mock.post(
        f"https://{host}/api/v3/botx/chats/remove_user",
        headers={"Authorization": "Bearer token", "Content-Type": "application/json"},
        json={
            "group_chat_id": "054af49e-5e18-4dca-ad73-4f96b6de63fa",
            "user_huids": ["f837dff4-d3ad-4b8d-a0a3-5c6ca9c747d1"],
        },
    ).mock(
        return_value=httpx.Response(
            HTTPStatus.OK,
            json={"status": "ok", "result": True},
        ),
    )

    built_bot = Bot(collectors=[HandlerCollector()], bot_accounts=[bot_account])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        await bot.remove_users_from_chat(
            bot_id=bot_id,
            chat_id=UUID("054af49e-5e18-4dca-ad73-4f96b6de63fa"),
            huids=[UUID("f837dff4-d3ad-4b8d-a0a3-5c6ca9c747d1")],
        )

    # - Assert -
    assert endpoint.called
