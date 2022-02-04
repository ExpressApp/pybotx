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
    ChatListItem,
    ChatTypes,
    HandlerCollector,
    lifespan_wrapper,
)

pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.mock_authorization,
    pytest.mark.usefixtures("respx_mock"),
]


async def test__list_chats__succeed(
    respx_mock: MockRouter,
    host: str,
    bot_id: UUID,
    bot_account: BotAccountWithSecret,
    datetime_formatter: Callable[[str], datetime],
) -> None:
    # - Arrange -
    endpoint = respx_mock.get(
        f"https://{host}/api/v3/botx/chats/list",
        headers={"Authorization": "Bearer token"},
    ).mock(
        return_value=httpx.Response(
            HTTPStatus.OK,
            json={
                "status": "ok",
                "result": [
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
                    },
                ],
            },
        ),
    )

    built_bot = Bot(collectors=[HandlerCollector()], bot_accounts=[bot_account])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        chats = await bot.list_chats(bot_id=bot_id)

    # - Assert -
    assert chats == [
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
        ),
    ]
    assert endpoint.called
