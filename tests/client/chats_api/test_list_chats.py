from datetime import datetime
from http import HTTPStatus
from typing import Any
from collections.abc import Callable
from uuid import UUID

import pytest
from respx.router import MockRouter

from pybotx import ChatListItem, ChatTypes
from pybotx.testkit import BotXRequest, assert_deep_equal, mock_botx, ok_payload

pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.mock_authorization,
    pytest.mark.usefixtures("respx_mock"),
]

ENDPOINT = "/api/v3/botx/chats/list"

REQUEST = BotXRequest(
    method="GET",
    path=ENDPOINT,
)


async def test__list_chats__succeed(
    respx_mock: MockRouter,
    host: str,
    bot_id: UUID,
    datetime_formatter: Callable[[str], datetime],
    bot_factory: Any,
) -> None:
    # - Arrange -
    endpoint = mock_botx(
        respx_mock,
        host,
        REQUEST,
        ok_payload(
            [
                {
                    "group_chat_id": "740cf331-d833-5250-b5a5-5b5cbc697ff5",
                    "chat_type": "group_chat",
                    "name": "Chat Name",
                    "description": "Desc",
                    "members": [
                        "6fafda2c-6505-57a5-a088-25ea5d1d0364",
                        "705df263-6bfd-536a-9d51-13524afaab5c",
                    ],
                    "inserted_at": "2019-08-29T11:22:48.358586Z",
                    "updated_at": "2019-08-30T21:02:10.453786Z",
                    "shared_history": False,
                },
            ],
        ),
        HTTPStatus.OK,
    )

    # - Act -
    async with bot_factory() as bot:
        chats = await bot.list_chats(bot_id=bot_id)

    # - Assert -
    assert_deep_equal(
        chats,
        [
            ChatListItem(
                chat_id=UUID("740cf331-d833-5250-b5a5-5b5cbc697ff5"),
                chat_type=ChatTypes.GROUP_CHAT,
                name="Chat Name",
                description="Desc",
                members=[
                    UUID("6fafda2c-6505-57a5-a088-25ea5d1d0364"),
                    UUID("705df263-6bfd-536a-9d51-13524afaab5c"),
                ],
                created_at=datetime_formatter("2019-08-29T11:22:48.358586Z"),
                updated_at=datetime_formatter("2019-08-30T21:02:10.453786Z"),
                shared_history=False,
            ),
        ],
    )
    assert endpoint.called


async def test__list_chats__unsupported_chats_types(
    respx_mock: MockRouter,
    host: str,
    bot_id: UUID,
    datetime_formatter: Callable[[str], datetime],
    loguru_caplog: pytest.LogCaptureFixture,
    bot_factory: Any,
) -> None:
    # - Arrange -
    endpoint = mock_botx(
        respx_mock,
        host,
        REQUEST,
        ok_payload(
            [
                {
                    "group_chat_id": "740cf331-d833-5250-b5a5-5b5cbc697ff5",
                    "chat_type": "group_chat",
                    "name": "Chat Name",
                    "description": "Desc",
                    "members": [
                        "6fafda2c-6505-57a5-a088-25ea5d1d0364",
                        "705df263-6bfd-536a-9d51-13524afaab5c",
                    ],
                    "inserted_at": "2019-08-29T11:22:48.358586Z",
                    "updated_at": "2019-08-30T21:02:10.453786Z",
                    "shared_history": False,
                },
                {
                    "group_chat_id": "c7faf797-5470-4d18-9b1c-379bb8b24d48",
                    "chat_type": "unsupported_chat_type",
                    "name": "Chat Name",
                    "description": "Desc",
                    "members": [
                        "0a2d036d-2257-4ffa-9cbc-e5bb8afe4d08",
                        "b54ace7a-a041-4dc0-ad83-1d5f8d635654",
                    ],
                    "inserted_at": "2019-08-29T11:22:48.358586Z",
                    "updated_at": "2019-08-30T21:02:10.453786Z",
                    "shared_history": False,
                },
            ],
        ),
        HTTPStatus.OK,
    )

    # - Act -
    async with bot_factory() as bot:
        chats = await bot.list_chats(bot_id=bot_id)

    # - Assert -
    assert "One or more unsupported chat types skipped" in loguru_caplog.text
    assert_deep_equal(
        chats,
        [
            ChatListItem(
                chat_id=UUID("740cf331-d833-5250-b5a5-5b5cbc697ff5"),
                chat_type=ChatTypes.GROUP_CHAT,
                name="Chat Name",
                description="Desc",
                members=[
                    UUID("6fafda2c-6505-57a5-a088-25ea5d1d0364"),
                    UUID("705df263-6bfd-536a-9d51-13524afaab5c"),
                ],
                created_at=datetime_formatter("2019-08-29T11:22:48.358586Z"),
                updated_at=datetime_formatter("2019-08-30T21:02:10.453786Z"),
                shared_history=False,
            ),
        ],
    )
    assert endpoint.called
