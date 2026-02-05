from http import HTTPStatus
from typing import Any, Type
from uuid import UUID

import pytest
from respx.router import MockRouter

from pybotx import (
    ChatLink,
    ChatLinkCreationError,
    ChatLinkCreationProhibitedError,
    ChatLinkTypes,
    ChatNotFoundError,
    InvalidBotXStatusCodeError,
)
from tests.testkit import (
    BotXRequest,
    assert_deep_equal,
    error_payload,
    mock_botx,
    ok_payload,
)

pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.mock_authorization,
    pytest.mark.usefixtures("respx_mock"),
]

ENDPOINT = "/api/v3/botx/chats/create_link"


@pytest.fixture
def chat_id() -> str:
    return "f102c2a6-bae5-5ade-9ace-10e5bd96102d"


async def test__create_chat_link__succeed(
    respx_mock: MockRouter,
    host: str,
    chat_id: str,
    bot_id: UUID,
    bot_factory: Any,
) -> None:
    # - Arrange -
    request = BotXRequest(
        method="POST",
        path=ENDPOINT,
        json={
            "chat_id": chat_id,
            "link": {
                "link_type": "public",
                "access_code": "1234",
                "link_ttl": 3600,
            },
        },
    )
    endpoint = mock_botx(
        respx_mock,
        host,
        request,
        ok_payload(
            {
                "url": "https://xlnk.ms/ASjalqtRVgGZQrtFCfJI8w",
                "link_type": "public",
                "access_code": "1234",
                "link_ttl": 3600,
            },
        ),
        HTTPStatus.OK,
    )

    # - Act -
    async with bot_factory() as bot:
        chat_link = await bot.create_chat_link(
            bot_id=bot_id,
            chat_id=UUID(chat_id),
            link_type=ChatLinkTypes.PUBLIC,
            access_code="1234",
            link_ttl=3600,
        )

    # - Assert -
    assert_deep_equal(
        chat_link,
        ChatLink(
            url="https://xlnk.ms/ASjalqtRVgGZQrtFCfJI8w",
            link_type=ChatLinkTypes.PUBLIC,
            access_code="1234",
            link_ttl=3600,
        ),
    )
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
    respx_mock: MockRouter,
    host: str,
    chat_id: str,
    bot_id: UUID,
    bot_factory: Any,
) -> None:
    # - Arrange -
    request = BotXRequest(
        method="POST",
        path=ENDPOINT,
        json={
            "chat_id": chat_id,
            "link": {
                "link_type": "public",
                "access_code": "1234",
                "link_ttl": 3600,
            },
        },
    )
    endpoint = mock_botx(
        respx_mock,
        host,
        request,
        return_json,
        response_status,
    )

    # - Act -
    async with bot_factory() as bot:
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
    respx_mock: MockRouter,
    host: str,
    chat_id: str,
    bot_id: UUID,
    bot_factory: Any,
) -> None:
    # - Arrange -
    request = BotXRequest(
        method="POST",
        path=ENDPOINT,
        json={
            "chat_id": chat_id,
            "link": {
                "link_type": "public",
                "access_code": "1234",
                "link_ttl": 3600,
            },
        },
    )
    endpoint = mock_botx(
        respx_mock,
        host,
        request,
        error_payload("unknown_reason"),
        HTTPStatus.INTERNAL_SERVER_ERROR,
    )

    # - Act -
    async with bot_factory() as bot:
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
