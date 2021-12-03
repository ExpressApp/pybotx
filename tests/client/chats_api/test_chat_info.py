from datetime import datetime as dt
from http import HTTPStatus
from typing import Callable
from uuid import UUID

import httpx
import pytest
import respx

from botx import (
    Bot,
    BotAccount,
    ChatInfo,
    ChatInfoMember,
    ChatNotFoundError,
    ChatTypes,
    HandlerCollector,
    UserKinds,
    lifespan_wrapper,
)


@respx.mock
@pytest.mark.asyncio
@pytest.mark.mock_authorization
async def test__chat_info__chat_not_found_error_raised(
    httpx_client: httpx.AsyncClient,
    host: str,
    bot_id: UUID,
    chat_id: UUID,
    bot_account: BotAccount,
) -> None:
    # - Arrange -
    endpoint = respx.get(
        f"https://{host}/api/v3/botx/chats/info",
        headers={"Authorization": "Bearer token"},
        params={"group_chat_id": str(chat_id)},
    ).mock(
        return_value=httpx.Response(
            HTTPStatus.NOT_FOUND,
            json={
                "status": "error",
                "reason": "chat_not_found",
                "errors": [],
                "error_data": {
                    "group_chat_id": "dcfa5a7c-7cc4-4c89-b6c0-80325604f9f4",
                    "error_description": "Chat with id dcfa5a7c-7cc4-4c89-b6c0-80325604f9f4 not found",
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
            await bot.chat_info(bot_id, chat_id)

    # - Assert -
    assert "chat_not_found" in str(exc.value)
    assert endpoint.called


@respx.mock
@pytest.mark.asyncio
@pytest.mark.mock_authorization
async def test__chat_info__succeed(
    httpx_client: httpx.AsyncClient,
    host: str,
    bot_id: UUID,
    chat_id: UUID,
    datetime_formatter: Callable[[str], dt],
    bot_account: BotAccount,
) -> None:
    # - Arrange -
    endpoint = respx.get(
        f"https://{host}/api/v3/botx/chats/info",
        headers={"Authorization": "Bearer token"},
        params={"group_chat_id": str(chat_id)},
    ).mock(
        return_value=httpx.Response(
            HTTPStatus.OK,
            json={
                "status": "ok",
                "result": {
                    "chat_type": "group_chat",
                    "creator": "6fafda2c-6505-57a5-a088-25ea5d1d0364",
                    "description": None,
                    "group_chat_id": str(chat_id),
                    "inserted_at": "2019-08-29T11:22:48.358586Z",
                    "members": [
                        {
                            "admin": True,
                            "user_huid": "6fafda2c-6505-57a5-a088-25ea5d1d0364",
                            "user_kind": "user",
                        },
                        {
                            "admin": False,
                            "user_huid": "705df263-6bfd-536a-9d51-13524afaab5c",
                            "user_kind": "botx",
                        },
                    ],
                    "name": "Group Chat Example",
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
        chat_info = await bot.chat_info(bot_id, chat_id)

    # - Assert -
    assert chat_info == ChatInfo(
        chat_type=ChatTypes.GROUP_CHAT,
        creator_id=UUID("6fafda2c-6505-57a5-a088-25ea5d1d0364"),
        description=None,
        chat_id=chat_id,
        created_at=datetime_formatter("2019-08-29T11:22:48.358586Z"),
        members=[
            ChatInfoMember(
                is_admin=True,
                huid=UUID("6fafda2c-6505-57a5-a088-25ea5d1d0364"),
                kind=UserKinds.RTS_USER,
            ),
            ChatInfoMember(
                is_admin=False,
                huid=UUID("705df263-6bfd-536a-9d51-13524afaab5c"),
                kind=UserKinds.BOT,
            ),
        ],
        name="Group Chat Example",
    )

    assert endpoint.called
