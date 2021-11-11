from http import HTTPStatus
from uuid import UUID

import httpx
import pytest
import respx

from botx import (
    Bot,
    BotAccount,
    ChatNotFoundError,
    HandlerCollector,
    PermissionDeniedError,
    lifespan_wrapper,
)


@respx.mock
@pytest.mark.asyncio
async def test__remove_users_from_chat__permission_denied_error_raised(
    httpx_client: httpx.AsyncClient,
    host: str,
    bot_id: UUID,
    chat_id: UUID,
    huid: UUID,
    bot_account: BotAccount,
    mock_authorization: None,
) -> None:
    # - Arrange -
    endpoint = respx.post(
        f"https://{host}/api/v3/botx/chats/remove_user",
        headers={"Authorization": "Bearer token", "Content-Type": "application/json"},
        json={
            "group_chat_id": str(chat_id),
            "user_huids": [str(huid)],
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

    built_bot = Bot(
        collectors=[HandlerCollector()],
        bot_accounts=[bot_account],
        httpx_client=httpx_client,
    )

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        with pytest.raises(PermissionDeniedError) as exc:
            await bot.remove_users_from_chat(bot_id, chat_id, huids=[huid])

    # - Assert -
    assert "no_permission_for_operation" in str(exc.value)
    assert endpoint.called


@respx.mock
@pytest.mark.asyncio
async def test__remove_users_from_chat__chat_noy_found_error_raised(
    httpx_client: httpx.AsyncClient,
    host: str,
    bot_id: UUID,
    chat_id: UUID,
    huid: UUID,
    bot_account: BotAccount,
    mock_authorization: None,
) -> None:
    # - Arrange -
    endpoint = respx.post(
        f"https://{host}/api/v3/botx/chats/remove_user",
        headers={"Authorization": "Bearer token", "Content-Type": "application/json"},
        json={
            "group_chat_id": str(chat_id),
            "user_huids": [str(huid)],
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

    built_bot = Bot(
        collectors=[HandlerCollector()],
        bot_accounts=[bot_account],
        httpx_client=httpx_client,
    )

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        with pytest.raises(ChatNotFoundError) as exc:
            await bot.remove_users_from_chat(bot_id, chat_id, huids=[huid])

    # - Assert -
    assert "chat_not_found" in str(exc.value)
    assert endpoint.called


@respx.mock
@pytest.mark.asyncio
async def test__remove_users_from_chat__succeed(
    httpx_client: httpx.AsyncClient,
    host: str,
    bot_id: UUID,
    chat_id: UUID,
    huid: UUID,
    bot_account: BotAccount,
    mock_authorization: None,
) -> None:
    # - Arrange -
    endpoint = respx.post(
        f"https://{host}/api/v3/botx/chats/remove_user",
        headers={"Authorization": "Bearer token", "Content-Type": "application/json"},
        json={
            "group_chat_id": str(chat_id),
            "user_huids": [str(huid)],
        },
    ).mock(
        return_value=httpx.Response(
            HTTPStatus.OK,
            json={"status": "ok", "result": True},
        ),
    )

    built_bot = Bot(
        collectors=[HandlerCollector()],
        bot_accounts=[bot_account],
        httpx_client=httpx_client,
    )

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        await bot.remove_users_from_chat(bot_id, chat_id, huids=[huid])

    # - Assert -
    assert endpoint.called
