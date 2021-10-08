from http import HTTPStatus
from uuid import UUID

import httpx
import pytest
import respx

from botx import Bot, BotAccount, ChatTypes, HandlerCollector, lifespan_wrapper
from botx.client.exceptions.chats import ChatCreationError, ChatCreationProhibited


@respx.mock
@pytest.mark.asyncio
async def test__create_chat__bot_have_no_permissions_raised(
    httpx_client: httpx.AsyncClient,
    host: str,
    bot_id: UUID,
    bot_account: BotAccount,
    mock_authorization: None,
) -> None:
    # - Arrange -
    endpoint = respx.post(
        f"https://{host}/api/v3/botx/chats/create",
        headers={"Authorization": "Bearer token", "Content-Type": "application/json"},
        json={
            "name": "Test chat name",
            "description": None,
            "chat_type": "group_chat",
            "members": [],
            "shared_history": False,
        },
    ).mock(
        return_value=httpx.Response(
            HTTPStatus.FORBIDDEN,
            json={
                "status": "error",
                "reason": "chat_creation_is_prohibited",
                "errors": ["This bot is not allowed to create chats"],
                "error_data": {
                    "bot_id": "a465f0f3-1354-491c-8f11-f400164295cb",
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
        with pytest.raises(ChatCreationProhibited) as exc:
            await bot.create_chat(
                bot_id,
                "Test chat name",
                ChatTypes.GROUP_CHAT,
                [],
            )

    # - Assert -
    assert endpoint.called
    assert "chat_creation_is_prohibited" in str(exc.value)


@respx.mock
@pytest.mark.asyncio
async def test__create_chat__botx_error_raised(
    httpx_client: httpx.AsyncClient,
    host: str,
    bot_id: UUID,
    bot_account: BotAccount,
    mock_authorization: None,
) -> None:
    # - Arrange -
    endpoint = respx.post(
        f"https://{host}/api/v3/botx/chats/create",
        headers={"Authorization": "Bearer token", "Content-Type": "application/json"},
        json={
            "name": "Test chat name",
            "description": None,
            "chat_type": "group_chat",
            "members": [],
            "shared_history": False,
        },
    ).mock(
        return_value=httpx.Response(
            HTTPStatus.UNPROCESSABLE_ENTITY,
            json={
                "status": "error",
                "reason": "|specified reason|",
                "errors": ["|specified errors|"],
                "error_data": {},
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
        with pytest.raises(ChatCreationError) as exc:
            await bot.create_chat(
                bot_id,
                "Test chat name",
                ChatTypes.GROUP_CHAT,
                [],
            )

    # - Assert -
    assert endpoint.called
    assert "specified reason" in str(exc.value)


@respx.mock
@pytest.mark.asyncio
async def test__create_chat__succeed(
    httpx_client: httpx.AsyncClient,
    host: str,
    bot_id: UUID,
    bot_account: BotAccount,
    chat_id: UUID,
    mock_authorization: None,
) -> None:
    # - Arrange -
    endpoint = respx.post(
        f"https://{host}/api/v3/botx/chats/create",
        headers={"Authorization": "Bearer token", "Content-Type": "application/json"},
        json={
            "name": "Test chat name",
            "description": None,
            "chat_type": "group_chat",
            "members": [],
            "shared_history": False,
        },
    ).mock(
        return_value=httpx.Response(
            HTTPStatus.OK,
            json={
                "status": "ok",
                "result": {"chat_id": str(chat_id)},
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
        created_chat_id = await bot.create_chat(
            bot_id,
            "Test chat name",
            ChatTypes.GROUP_CHAT,
            [],
        )

    # - Assert -
    assert created_chat_id == chat_id
    assert endpoint.called
