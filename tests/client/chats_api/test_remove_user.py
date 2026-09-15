from http import HTTPStatus
from typing import Any
from collections.abc import Sequence
from uuid import UUID

import pytest
from respx.router import MockRouter

from pybotx import ChatNotFoundError, PermissionDeniedError
from tests.testkit import BotXRequest, error_payload, mock_botx, ok_payload

pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.mock_authorization,
    pytest.mark.usefixtures("respx_mock"),
]

ENDPOINT = "/api/v3/botx/chats/remove_user"

REQUEST = BotXRequest(
    method="POST",
    path=ENDPOINT,
    json={
        "group_chat_id": "054af49e-5e18-4dca-ad73-4f96b6de63fa",
        "user_huids": ["f837dff4-d3ad-4b8d-a0a3-5c6ca9c747d1"],
    },
)


@pytest.mark.parametrize(
    ("response_status", "response_json", "expected_exc", "expected_fragments"),
    [
        (
            HTTPStatus.NOT_FOUND,
            error_payload(
                "chat_not_found",
                errors=["Chat not found"],
                error_data={
                    "group_chat_id": "dcfa5a7c-7cc4-4c89-b6c0-80325604f9f4",
                },
            ),
            ChatNotFoundError,
            ("chat_not_found",),
        ),
        (
            HTTPStatus.FORBIDDEN,
            error_payload(
                "no_permission_for_operation",
                errors=["Sender is not chat admin"],
                error_data={
                    "group_chat_id": "dcfa5a7c-7cc4-4c89-b6c0-80325604f9f4",
                    "sender": "a465f0f3-1354-491c-8f11-f400164295cb",
                },
            ),
            PermissionDeniedError,
            ("no_permission_for_operation",),
        ),
    ],
)
async def test__remove_users_from_chat__error_response(
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
    endpoint = mock_botx(respx_mock, host, REQUEST, response_json, response_status)

    # - Act -
    async with bot_factory() as bot:
        with pytest.raises(expected_exc) as exc:
            await bot.remove_users_from_chat(
                bot_id=bot_id,
                chat_id=UUID("054af49e-5e18-4dca-ad73-4f96b6de63fa"),
                huids=[UUID("f837dff4-d3ad-4b8d-a0a3-5c6ca9c747d1")],
            )

    # - Assert -
    for fragment in expected_fragments:
        assert fragment in str(exc.value)
    assert endpoint.called


async def test__remove_users_from_chat__succeed(
    respx_mock: MockRouter,
    host: str,
    bot_id: UUID,
    bot_factory: Any,
) -> None:
    # - Arrange -
    endpoint = mock_botx(
        respx_mock,
        host,
        REQUEST,
        ok_payload(True),
        HTTPStatus.OK,
    )

    # - Act -
    async with bot_factory() as bot:
        await bot.remove_users_from_chat(
            bot_id=bot_id,
            chat_id=UUID("054af49e-5e18-4dca-ad73-4f96b6de63fa"),
            huids=[UUID("f837dff4-d3ad-4b8d-a0a3-5c6ca9c747d1")],
        )

    # - Assert -
    assert endpoint.called
