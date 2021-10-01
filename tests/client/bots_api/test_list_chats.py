from datetime import datetime
from http import HTTPStatus
from typing import Callable
from uuid import UUID

import httpx
import pytest
import respx
from pydantic import BaseModel

from botx import Bot, BotAccount, ChatTypes, HandlerCollector, lifespan_wrapper
from botx.client.chats_api.list_chats import ChatListItem


@pytest.fixture
def datetime_formatter() -> Callable[[str], datetime]:
    class DateTimeFormatter(BaseModel):  # noqa: WPS431
        value: datetime

    def factory(dt_str: str) -> datetime:
        return DateTimeFormatter(value=dt_str).value

    return factory


@respx.mock
@pytest.mark.asyncio
async def test_list_chats(
    httpx_client: httpx.AsyncClient,
    host: str,
    bot_id: UUID,
    bot_account: BotAccount,
    datetime_formatter: Callable[[str], datetime],
    mock_authorization: None,
) -> None:
    # - Arrange -
    endpoint = respx.get(
        f"https://{host}/api/v3/botx/chats/list",
        headers={"Authorization": "Bearer token", "Content-Type": "application/json"},
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

    built_bot = Bot(
        collectors=[HandlerCollector()],
        bot_accounts=[bot_account],
        httpx_client=httpx_client,
    )

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        chats = await bot.list_chats(bot_id)

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
            inserted_at=datetime_formatter("2019-08-29T11:22:48.358586Z"),
            updated_at=datetime_formatter("2019-08-30T21:02:10.453786Z"),
        ),
    ]
    assert endpoint.called
