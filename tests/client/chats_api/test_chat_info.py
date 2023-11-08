from datetime import datetime as dt
from http import HTTPStatus
from typing import Callable
from uuid import UUID

import httpx
import pytest
from respx.router import MockRouter

from pybotx import (
    Bot,
    BotAccountWithSecret,
    ChatInfo,
    ChatInfoMember,
    ChatNotFoundError,
    ChatTypes,
    HandlerCollector,
    UserKinds,
    lifespan_wrapper,
)

pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.mock_authorization,
    pytest.mark.usefixtures("respx_mock"),
]


async def test__chat_info__chat_not_found_error_raised(
    respx_mock: MockRouter,
    host: str,
    bot_id: UUID,
    bot_account: BotAccountWithSecret,
) -> None:
    # - Arrange -
    endpoint = respx_mock.get(
        f"https://{host}/api/v3/botx/chats/info",
        headers={"Authorization": "Bearer token"},
        params={"group_chat_id": "054af49e-5e18-4dca-ad73-4f96b6de63fa"},
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

    built_bot = Bot(collectors=[HandlerCollector()], bot_accounts=[bot_account])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        with pytest.raises(ChatNotFoundError) as exc:
            await bot.chat_info(
                bot_id=bot_id,
                chat_id=UUID("054af49e-5e18-4dca-ad73-4f96b6de63fa"),
            )

    # - Assert -
    assert "chat_not_found" in str(exc.value)
    assert endpoint.called


async def test__chat_info__succeed(
    respx_mock: MockRouter,
    host: str,
    bot_id: UUID,
    datetime_formatter: Callable[[str], dt],
    bot_account: BotAccountWithSecret,
) -> None:
    # - Arrange -
    endpoint = respx_mock.get(
        f"https://{host}/api/v3/botx/chats/info",
        headers={"Authorization": "Bearer token"},
        params={"group_chat_id": "054af49e-5e18-4dca-ad73-4f96b6de63fa"},
    ).mock(
        return_value=httpx.Response(
            HTTPStatus.OK,
            json={
                "status": "ok",
                "result": {
                    "chat_type": "group_chat",
                    "creator": "6fafda2c-6505-57a5-a088-25ea5d1d0364",
                    "description": None,
                    "group_chat_id": "054af49e-5e18-4dca-ad73-4f96b6de63fa",
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
                    "shared_history": False,
                },
            },
        ),
    )

    built_bot = Bot(collectors=[HandlerCollector()], bot_accounts=[bot_account])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        chat_info = await bot.chat_info(
            bot_id=bot_id,
            chat_id=UUID("054af49e-5e18-4dca-ad73-4f96b6de63fa"),
        )

    # - Assert -
    assert chat_info == ChatInfo(
        chat_type=ChatTypes.GROUP_CHAT,
        creator_id=UUID("6fafda2c-6505-57a5-a088-25ea5d1d0364"),
        description=None,
        chat_id=UUID("054af49e-5e18-4dca-ad73-4f96b6de63fa"),
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
        shared_history=False,
    )

    assert endpoint.called


async def test__chat_info__skipped_members(
    respx_mock: MockRouter,
    host: str,
    bot_id: UUID,
    datetime_formatter: Callable[[str], dt],
    bot_account: BotAccountWithSecret,
    loguru_caplog: pytest.LogCaptureFixture,
) -> None:
    # - Arrange -
    endpoint = respx_mock.get(
        f"https://{host}/api/v3/botx/chats/info",
        headers={"Authorization": "Bearer token"},
        params={"group_chat_id": "054af49e-5e18-4dca-ad73-4f96b6de63fa"},
    ).mock(
        return_value=httpx.Response(
            HTTPStatus.OK,
            json={
                "status": "ok",
                "result": {
                    "chat_type": "group_chat",
                    "creator": "6fafda2c-6505-57a5-a088-25ea5d1d0364",
                    "description": None,
                    "group_chat_id": "054af49e-5e18-4dca-ad73-4f96b6de63fa",
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
                        {
                            "admin": False,
                            "user_huid": "0843a8a8-6d56-4ce6-92aa-13dc36bd9ede",
                            "user_kind": "unsupported_user_type",
                        },
                    ],
                    "name": "Group Chat Example",
                    "shared_history": False,
                },
            },
        ),
    )

    built_bot = Bot(collectors=[HandlerCollector()], bot_accounts=[bot_account])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        chat_info = await bot.chat_info(
            bot_id=bot_id,
            chat_id=UUID("054af49e-5e18-4dca-ad73-4f96b6de63fa"),
        )

    # - Assert -
    assert chat_info == ChatInfo(
        chat_type=ChatTypes.GROUP_CHAT,
        creator_id=UUID("6fafda2c-6505-57a5-a088-25ea5d1d0364"),
        description=None,
        chat_id=UUID("054af49e-5e18-4dca-ad73-4f96b6de63fa"),
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
        shared_history=False,
    )
    assert "One or more unsupported user types skipped" in loguru_caplog.text
    assert endpoint.called


async def test__open_channel_info__succeed(
    respx_mock: MockRouter,
    host: str,
    bot_id: UUID,
    datetime_formatter: Callable[[str], dt],
    bot_account: BotAccountWithSecret,
) -> None:
    # - Arrange -
    endpoint = respx_mock.get(
        f"https://{host}/api/v3/botx/chats/info",
        headers={"Authorization": "Bearer token"},
        params={"group_chat_id": "e53d5080-68f7-5050-bb4f-005efd375612"},
    ).mock(
        return_value=httpx.Response(
            HTTPStatus.OK,
            json={
                "status": "ok",
                "result": {
                    "chat_type": "channel",
                    "creator": None,
                    "description": None,
                    "group_chat_id": "e53d5080-68f7-5050-bb4f-005efd375612",
                    "inserted_at": "2023-10-26T07:49:53.821672Z",
                    "members": [
                        {
                            "admin": True,
                            "server_id": "a619fcfa-a19b-5256-a592-9b0e75ca0896",
                            "user_huid": "6fafda2c-6505-57a5-a088-25ea5d1d0364",
                            "user_kind": "cts_user",
                        },
                        {
                            "admin": False,
                            "user_huid": "705df263-6bfd-536a-9d51-13524afaab5c",
                            "server_id": "a619fcfa-a19b-5256-a592-9b0e75ca0896",
                            "user_kind": "botx",
                        },
                    ],
                    "name": "Open Channel Example",
                    "shared_history": False,
                    "updated_at": "2023-10-26T08:09:30.721566Z",
                },
            },
        ),
    )

    built_bot = Bot(collectors=[HandlerCollector()], bot_accounts=[bot_account])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        chat_info = await bot.chat_info(
            bot_id=bot_id,
            chat_id=UUID("e53d5080-68f7-5050-bb4f-005efd375612"),
        )

    # - Assert -
    assert chat_info == ChatInfo(
        chat_type=ChatTypes.CHANNEL,
        creator_id=None,
        description=None,
        chat_id=UUID("e53d5080-68f7-5050-bb4f-005efd375612"),
        created_at=datetime_formatter("2023-10-26T07:49:53.821672Z"),
        members=[
            ChatInfoMember(
                is_admin=True,
                huid=UUID("6fafda2c-6505-57a5-a088-25ea5d1d0364"),
                kind=UserKinds.CTS_USER,
            ),
            ChatInfoMember(
                is_admin=False,
                huid=UUID("705df263-6bfd-536a-9d51-13524afaab5c"),
                kind=UserKinds.BOT,
            ),
        ],
        name="Open Channel Example",
        shared_history=False,
    )

    assert endpoint.called
