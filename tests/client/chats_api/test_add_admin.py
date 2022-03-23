from http import HTTPStatus
from uuid import UUID

import httpx
import pytest
from respx.router import MockRouter

from pybotx import (
    Bot,
    BotAccountWithSecret,
    CantUpdatePersonalChatError,
    ChatNotFoundError,
    HandlerCollector,
    InvalidBotXStatusCodeError,
    InvalidUsersListError,
    PermissionDeniedError,
    lifespan_wrapper,
)

pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.mock_authorization,
    pytest.mark.usefixtures("respx_mock"),
]


async def test__promote_to_chat_admins__unexpected_bad_request_error_raised(
    respx_mock: MockRouter,
    host: str,
    bot_id: UUID,
    bot_account: BotAccountWithSecret,
) -> None:
    # - Arrange -
    endpoint = respx_mock.post(
        f"https://{host}/api/v3/botx/chats/add_admin",
        headers={"Authorization": "Bearer token", "Content-Type": "application/json"},
        json={
            "group_chat_id": "054af49e-5e18-4dca-ad73-4f96b6de63fa",
            "user_huids": ["f837dff4-d3ad-4b8d-a0a3-5c6ca9c747d1"],
        },
    ).mock(
        return_value=httpx.Response(
            HTTPStatus.BAD_REQUEST,
            json={
                "status": "error",
                "reason": "some_reason",
                "errors": [],
                "error_data": {},
            },
        ),
    )

    built_bot = Bot(collectors=[HandlerCollector()], bot_accounts=[bot_account])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        with pytest.raises(InvalidBotXStatusCodeError) as exc:
            await bot.promote_to_chat_admins(
                bot_id=bot_id,
                chat_id=UUID("054af49e-5e18-4dca-ad73-4f96b6de63fa"),
                huids=[UUID("f837dff4-d3ad-4b8d-a0a3-5c6ca9c747d1")],
            )

    # - Assert -
    assert "some_reason" in str(exc.value)
    assert endpoint.called


async def test__promote_to_chat_admins__cant_update_personal_chat_error_raised(
    respx_mock: MockRouter,
    host: str,
    bot_id: UUID,
    bot_account: BotAccountWithSecret,
) -> None:
    # - Arrange -
    endpoint = respx_mock.post(
        f"https://{host}/api/v3/botx/chats/add_admin",
        headers={"Authorization": "Bearer token", "Content-Type": "application/json"},
        json={
            "group_chat_id": "054af49e-5e18-4dca-ad73-4f96b6de63fa",
            "user_huids": ["f837dff4-d3ad-4b8d-a0a3-5c6ca9c747d1"],
        },
    ).mock(
        return_value=httpx.Response(
            HTTPStatus.BAD_REQUEST,
            json={
                "status": "error",
                "reason": "chat_members_not_modifiable",
                "errors": [],
                "error_data": {},
            },
        ),
    )

    built_bot = Bot(collectors=[HandlerCollector()], bot_accounts=[bot_account])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        with pytest.raises(CantUpdatePersonalChatError) as exc:
            await bot.promote_to_chat_admins(
                bot_id=bot_id,
                chat_id=UUID("054af49e-5e18-4dca-ad73-4f96b6de63fa"),
                huids=[UUID("f837dff4-d3ad-4b8d-a0a3-5c6ca9c747d1")],
            )

    # - Assert -
    assert "chat_members_not_modifiable" in str(exc.value)
    assert "Personal chat couldn't have admins" in str(exc.value)
    assert endpoint.called


async def test__promote_to_chat_admins__invalid_users_list_error_raised(
    respx_mock: MockRouter,
    host: str,
    bot_id: UUID,
    bot_account: BotAccountWithSecret,
) -> None:
    # - Arrange -
    endpoint = respx_mock.post(
        f"https://{host}/api/v3/botx/chats/add_admin",
        headers={"Authorization": "Bearer token", "Content-Type": "application/json"},
        json={
            "group_chat_id": "054af49e-5e18-4dca-ad73-4f96b6de63fa",
            "user_huids": ["f837dff4-d3ad-4b8d-a0a3-5c6ca9c747d1"],
        },
    ).mock(
        return_value=httpx.Response(
            HTTPStatus.BAD_REQUEST,
            json={
                "status": "error",
                "reason": "admins_not_changed",
                "errors": ["Admins have not changed"],
                "error_data": {
                    "group_chat_id": "dcfa5a7c-7cc4-4c89-b6c0-80325604f9f4",
                },
            },
        ),
    )

    built_bot = Bot(collectors=[HandlerCollector()], bot_accounts=[bot_account])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        with pytest.raises(InvalidUsersListError) as exc:
            await bot.promote_to_chat_admins(
                bot_id=bot_id,
                chat_id=UUID("054af49e-5e18-4dca-ad73-4f96b6de63fa"),
                huids=[UUID("f837dff4-d3ad-4b8d-a0a3-5c6ca9c747d1")],
            )

    # - Assert -
    assert "admins_not_changed" in str(exc.value)
    assert "Specified users are already admins or missing from chat" in str(exc.value)
    assert endpoint.called


async def test__promote_to_chat_admins__permission_denied_error_raised(
    respx_mock: MockRouter,
    host: str,
    bot_id: UUID,
    bot_account: BotAccountWithSecret,
) -> None:
    # - Arrange -
    endpoint = respx_mock.post(
        f"https://{host}/api/v3/botx/chats/add_admin",
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
            await bot.promote_to_chat_admins(
                bot_id=bot_id,
                chat_id=UUID("054af49e-5e18-4dca-ad73-4f96b6de63fa"),
                huids=[UUID("f837dff4-d3ad-4b8d-a0a3-5c6ca9c747d1")],
            )

    # - Assert -
    assert "no_permission_for_operation" in str(exc.value)
    assert endpoint.called


async def test__promote_to_chat_admins__chat_not_found_error_raised(
    respx_mock: MockRouter,
    host: str,
    bot_id: UUID,
    bot_account: BotAccountWithSecret,
) -> None:
    # - Arrange -
    endpoint = respx_mock.post(
        f"https://{host}/api/v3/botx/chats/add_admin",
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
            await bot.promote_to_chat_admins(
                bot_id=bot_id,
                chat_id=UUID("054af49e-5e18-4dca-ad73-4f96b6de63fa"),
                huids=[UUID("f837dff4-d3ad-4b8d-a0a3-5c6ca9c747d1")],
            )

    # - Assert -
    assert "chat_not_found" in str(exc.value)
    assert endpoint.called


async def test__promote_to_chat_admins__succeed(
    respx_mock: MockRouter,
    host: str,
    bot_id: UUID,
    bot_account: BotAccountWithSecret,
) -> None:
    # - Arrange -
    endpoint = respx_mock.post(
        f"https://{host}/api/v3/botx/chats/add_admin",
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
        await bot.promote_to_chat_admins(
            bot_id=bot_id,
            chat_id=UUID("054af49e-5e18-4dca-ad73-4f96b6de63fa"),
            huids=[UUID("f837dff4-d3ad-4b8d-a0a3-5c6ca9c747d1")],
        )

    # - Assert -
    assert endpoint.called
