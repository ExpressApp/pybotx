from collections.abc import Callable
from http import HTTPStatus
from typing import Any, Type
from uuid import UUID

import httpx
import pytest
from respx import Route
from respx.router import MockRouter

from pybotx import (
    Bot,
    BotAccountWithSecret,
    ChatLinkCreationError,
    ChatLinkCreationProhibitedError,
    ChatLinkTypes,
    ChatNotFoundError,
    HandlerCollector,
    InvalidBotXStatusCodeError,
    lifespan_wrapper,
)

pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.mock_authorization,
    pytest.mark.usefixtures("respx_mock"),
]

ENDPOINT = "api/v3/botx/chats/create_link"


@pytest.fixture
def chat_id() -> str:
    return "f102c2a6-bae5-5ade-9ace-10e5bd96102d"


@pytest.fixture
def create_mocked_endpoint(
    respx_mock: MockRouter,
    host: str,
    chat_id: str,
) -> Callable[[dict[str, Any], int], Route]:
    def mocked_endpoint(json_response: dict[str, Any], status_code: int) -> Route:
        return respx_mock.post(
            f"https://{host}/{ENDPOINT}",
            headers={
                "Authorization": "Bearer token",
                "Content-Type": "application/json",
            },
            json={
                "chat_id": chat_id,
                "link": {
                    "link_type": "public",
                    "access_code": "1234",
                    "link_ttl": 3600,
                },
            },
        ).mock(return_value=httpx.Response(status_code, json=json_response))

    return mocked_endpoint


async def test__create_chat_link__succeed(
    create_mocked_endpoint: Callable[[dict[str, Any], int], Route],
    chat_id: str,
    bot_id: UUID,
    bot_account: BotAccountWithSecret,
) -> None:
    # - Arrange -
    endpoint = create_mocked_endpoint(
        {
            "status": "ok",
            "result": {
                "url": "https://xlnk.ms/ASjalqtRVgGZQrtFCfJI8w",
                "link_type": "public",
                "access_code": "1234",
                "link_ttl": 3600,
            },
        },
        HTTPStatus.OK,
    )

    built_bot = Bot(collectors=[HandlerCollector()], bot_accounts=[bot_account])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        chat_link = await bot.create_chat_link(
            bot_id=bot_id,
            chat_id=UUID(chat_id),
            link_type=ChatLinkTypes.PUBLIC,
            access_code="1234",
            link_ttl=3600,
        )

    # - Assert -
    assert chat_link.url == "https://xlnk.ms/ASjalqtRVgGZQrtFCfJI8w"
    assert chat_link.link_type == ChatLinkTypes.PUBLIC
    assert chat_link.access_code == "1234"
    assert chat_link.link_ttl == 3600
    assert endpoint.called


@pytest.mark.parametrize(
    ("return_json", "response_status", "expected_exc_type"),
    (
        (
            {
                "status": "error",
                "reason": "chat_not_found",
                "errors": [],
                "error_data": {},
            },
            HTTPStatus.NOT_FOUND,
            ChatNotFoundError,
        ),
        (
            {
                "status": "error",
                "reason": "no_permission_for_operation",
                "errors": [],
                "error_data": {},
            },
            HTTPStatus.FORBIDDEN,
            ChatLinkCreationProhibitedError,
        ),
        (
            {
                "status": "error",
                "reason": "error_from_messaging_service",
                "errors": [],
                "error_data": {
                    "error_description": "Messaging service returns error",
                    "group_chat_id": "dcfa5a7c-7cc4-4c89-b6c0-80325604f9f4",
                    "reason": "some_error",
                },
            },
            HTTPStatus.INTERNAL_SERVER_ERROR,
            ChatLinkCreationError,
        ),
    ),
)
async def test__create_chat_link__error_response(
    return_json: dict[str, Any],
    response_status: int,
    expected_exc_type: Type[Exception],
    create_mocked_endpoint: Callable[[dict[str, Any], int], Route],
    chat_id: str,
    bot_id: UUID,
    bot_account: BotAccountWithSecret,
) -> None:
    # - Arrange -
    endpoint = create_mocked_endpoint(return_json, response_status)

    built_bot = Bot(collectors=[HandlerCollector()], bot_accounts=[bot_account])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        with pytest.raises(expected_exc_type):
            await bot.create_chat_link(
                bot_id=bot_id,
                chat_id=UUID(chat_id),
                link_type=ChatLinkTypes.PUBLIC,
                access_code="1234",
                link_ttl=3600,
            )

    # - Assert -
    assert endpoint.called


async def test__create_chat_link__unknown_server_error_reason(
    create_mocked_endpoint: Callable[[dict[str, Any], int], Route],
    chat_id: str,
    bot_id: UUID,
    bot_account: BotAccountWithSecret,
) -> None:
    # - Arrange -
    endpoint = create_mocked_endpoint(
        {
            "status": "error",
            "reason": "unknown_reason",
            "errors": [],
            "error_data": {},
        },
        HTTPStatus.INTERNAL_SERVER_ERROR,
    )

    built_bot = Bot(collectors=[HandlerCollector()], bot_accounts=[bot_account])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        with pytest.raises(InvalidBotXStatusCodeError):
            await bot.create_chat_link(
                bot_id=bot_id,
                chat_id=UUID(chat_id),
                link_type=ChatLinkTypes.PUBLIC,
                access_code="1234",
                link_ttl=3600,
            )

    # - Assert -
    assert endpoint.called
