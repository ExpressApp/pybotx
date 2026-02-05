# tests/client/chats_api/test_personal_chat.py

from datetime import datetime as dt
from http import HTTPStatus
from typing import Any
from collections.abc import Callable, Sequence
from uuid import UUID

import pytest
from respx.router import MockRouter

from pybotx import ChatNotFoundError
from tests.client.chats_api.factories import (
    APIPersonalChatResponseFactory,
    ChatInfoFactory,
)
from tests.testkit import BotXRequest, assert_deep_equal, error_payload, mock_botx

pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.mock_authorization,
    pytest.mark.usefixtures("respx_mock"),
]

ENDPOINT = "/api/v1/botx/chats/personal"


@pytest.mark.parametrize(
    ("response_status", "response_json", "expected_exc", "expected_fragments"),
    [
        (
            HTTPStatus.NOT_FOUND,
            error_payload(
                "chat_not_found",
                error_data={
                    "user_huid": "dcfa5a7c-7cc4-4c89-b6c0-80325604f9f4",
                    "error_description": "Chat with user dcfa5a7c-7cc4-4c89-b6c0-80325604f9f4 not found",
                },
            ),
            ChatNotFoundError,
            ("chat_not_found",),
        ),
    ],
)
async def test__personal_chat__error_response(
    response_status: int,
    response_json: dict[str, Any],
    expected_exc: type[Exception],
    expected_fragments: Sequence[str],
    respx_mock: MockRouter,
    host: str,
    bot_id: UUID,
    bot_factory: Any,
) -> None:
    # - Arrange -
    request = BotXRequest(
        method="GET",
        path=ENDPOINT,
        params={"user_huid": "dcfa5a7c-7cc4-4c89-b6c0-80325604f9f4"},
    )
    endpoint = mock_botx(respx_mock, host, request, response_json, response_status)

    # - Act -
    async with bot_factory() as bot:
        with pytest.raises(expected_exc) as exc:
            await bot.personal_chat(
                bot_id=bot_id,
                user_huid=UUID("dcfa5a7c-7cc4-4c89-b6c0-80325604f9f4"),
            )

    # - Assert -
    for fragment in expected_fragments:
        assert fragment in str(exc.value)
    assert endpoint.called


async def test__personal_chat__succeed(
    respx_mock: MockRouter,
    host: str,
    bot_id: UUID,
    datetime_formatter: Callable[[str], dt],
    bot_factory: Any,
) -> None:
    # - Arrange -
    api_response: Any = APIPersonalChatResponseFactory()  # type: ignore[no-untyped-call]

    request = BotXRequest(
        method="GET",
        path=ENDPOINT,
        params={"user_huid": "6fafda2c-6505-57a5-a088-25ea5d1d0364"},
    )
    endpoint = mock_botx(respx_mock, host, request, api_response, HTTPStatus.OK)

    # - Act -
    async with bot_factory() as bot:
        chat_info = await bot.personal_chat(
            bot_id=bot_id,
            user_huid=UUID("6fafda2c-6505-57a5-a088-25ea5d1d0364"),
        )

    # - Assert -
    expected_chat_info = ChatInfoFactory(
        created_at=datetime_formatter("2019-08-29T11:22:48.358586Z"),
    )  # type: ignore[no-untyped-call]

    assert_deep_equal(chat_info, expected_chat_info)
    assert endpoint.called


async def test__personal_chat__skipped_members(
    respx_mock: MockRouter,
    host: str,
    bot_id: UUID,
    datetime_formatter: Callable[[str], dt],
    loguru_caplog: pytest.LogCaptureFixture,
    bot_factory: Any,
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

    request = BotXRequest(
        method="GET",
        path=ENDPOINT,
        params={"user_huid": "6fafda2c-6505-57a5-a088-25ea5d1d0364"},
    )
    endpoint = mock_botx(respx_mock, host, request, api_response, HTTPStatus.OK)

    # - Act -
    async with bot_factory() as bot:
        chat_info = await bot.personal_chat(
            bot_id=bot_id,
            user_huid=UUID("6fafda2c-6505-57a5-a088-25ea5d1d0364"),
        )

    # - Assert -
    expected_chat_info = ChatInfoFactory(
        created_at=datetime_formatter("2019-08-29T11:22:48.358586Z"),
    )  # type: ignore[no-untyped-call]

    assert_deep_equal(chat_info, expected_chat_info)
    assert "Unsupported user type skipped in members list" in loguru_caplog.text
    assert endpoint.called
