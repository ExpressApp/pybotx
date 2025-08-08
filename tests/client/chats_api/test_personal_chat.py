# tests/client/chats_api/test_personal_chat.py

from datetime import datetime as dt
from http import HTTPStatus
from typing import Callable, Any
from uuid import UUID

import httpx
import pytest
from deepdiff import DeepDiff
from respx.router import MockRouter

from pybotx import (
    Bot,
    BotAccountWithSecret,
    ChatNotFoundError,
    HandlerCollector,
    lifespan_wrapper,
)
from tests.client.chats_api.factories import (
    APIPersonalChatResponseFactory,
    ChatInfoFactory,
)

pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.mock_authorization,
    pytest.mark.usefixtures("respx_mock"),
]


async def test__personal_chat__chat_not_found_error_raised(
    respx_mock: MockRouter,
    host: str,
    bot_id: UUID,
    bot_account: BotAccountWithSecret,
) -> None:
    # - Arrange -
    endpoint = respx_mock.get(
        f"https://{host}/api/v1/botx/chats/personal",
        headers={"Authorization": "Bearer token"},
        params={"user_huid": "dcfa5a7c-7cc4-4c89-b6c0-80325604f9f4"},
    ).mock(
        return_value=httpx.Response(
            HTTPStatus.NOT_FOUND,
            json={
                "status": "error",
                "reason": "chat_not_found",
                "errors": [],
                "error_data": {
                    "user_huid": "dcfa5a7c-7cc4-4c89-b6c0-80325604f9f4",
                    "error_description": "Chat with user dcfa5a7c-7cc4-4c89-b6c0-80325604f9f4 not found",
                },
            },
        ),
    )

    built_bot = Bot(collectors=[HandlerCollector()], bot_accounts=[bot_account])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        with pytest.raises(ChatNotFoundError) as exc:
            await bot.personal_chat(
                bot_id=bot_id,
                user_huid=UUID("dcfa5a7c-7cc4-4c89-b6c0-80325604f9f4"),
            )

    # - Assert -
    assert "chat_not_found" in str(exc.value)
    assert endpoint.called


async def test__personal_chat__succeed(
    respx_mock: MockRouter,
    host: str,
    bot_id: UUID,
    datetime_formatter: Callable[[str], dt],
    bot_account: BotAccountWithSecret,
) -> None:
    # - Arrange -
    api_response: Any = APIPersonalChatResponseFactory()  # type: ignore[no-untyped-call]

    endpoint = respx_mock.get(
        f"https://{host}/api/v1/botx/chats/personal",
        headers={"Authorization": "Bearer token"},
        params={"user_huid": "6fafda2c-6505-57a5-a088-25ea5d1d0364"},
    ).mock(
        return_value=httpx.Response(
            HTTPStatus.OK,
            json=api_response,
        ),
    )

    built_bot = Bot(collectors=[HandlerCollector()], bot_accounts=[bot_account])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        chat_info = await bot.personal_chat(
            bot_id=bot_id,
            user_huid=UUID("6fafda2c-6505-57a5-a088-25ea5d1d0364"),
        )

    # - Assert -
    expected_chat_info = ChatInfoFactory(
        created_at=datetime_formatter("2019-08-29T11:22:48.358586Z"),
    )  # type: ignore[no-untyped-call]

    diff = DeepDiff(chat_info, expected_chat_info)
    assert diff == {}, diff

    assert endpoint.called


async def test__personal_chat__skipped_members(
    respx_mock: MockRouter,
    host: str,
    bot_id: UUID,
    datetime_formatter: Callable[[str], dt],
    bot_account: BotAccountWithSecret,
    loguru_caplog: pytest.LogCaptureFixture,
) -> None:
    # - Arrange -
    api_response: Any = APIPersonalChatResponseFactory()  # type: ignore[no-untyped-call]
    # Add an unsupported user type to the members list
    api_response["result"]["members"].append(
        {
            "admin": "not-a-bool",
            "user_huid": "5f5c9b04-f7d2-45a6-b36b-0123456789ab",
            "user_kind": "unsupported_user_type",
        }
    )

    endpoint = respx_mock.get(
        f"https://{host}/api/v1/botx/chats/personal",
        headers={"Authorization": "Bearer token"},
        params={"user_huid": "6fafda2c-6505-57a5-a088-25ea5d1d0364"},
    ).mock(
        return_value=httpx.Response(
            HTTPStatus.OK,
            json=api_response,
        ),
    )

    built_bot = Bot(collectors=[HandlerCollector()], bot_accounts=[bot_account])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        chat_info = await bot.personal_chat(
            bot_id=bot_id,
            user_huid=UUID("6fafda2c-6505-57a5-a088-25ea5d1d0364"),
        )

    # - Assert -
    expected_chat_info = ChatInfoFactory(
        created_at=datetime_formatter("2019-08-29T11:22:48.358586Z"),
    )  # type: ignore[no-untyped-call]

    diff = DeepDiff(chat_info, expected_chat_info)
    assert diff == {}, diff

    assert "Unsupported user type skipped in members list" in loguru_caplog.text
    assert endpoint.called
