from http import HTTPStatus
from typing import Any, Sequence, Type
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

ENDPOINT = "/api/v3/botx/chats/unpin_message"

REQUEST = BotXRequest(
    method="POST",
    path=ENDPOINT,
    json={
        "chat_id": "054af49e-5e18-4dca-ad73-4f96b6de63fa",
    },
)


@pytest.mark.parametrize(
    ("response_status", "response_json", "expected_exc", "expected_fragments"),
    [
        (
            HTTPStatus.FORBIDDEN,
            error_payload(
                "no_permission_for_operation",
                error_data={
                    "bot_id": "f9e1c958-bf81-564e-bff2-a2943869af15",
                    "error_description": "Bot doesn't have permission for this operation in current chat",
                    "group_chat_id": "5680c26a-07a5-5b40-a6ff-f5e7e68fed25",
                },
            ),
            PermissionDeniedError,
            ("no_permission_for_operation",),
        ),
        (
            HTTPStatus.NOT_FOUND,
            error_payload(
                "chat_not_found",
                error_data={
                    "error_description": "Chat with specified id not found",
                    "group_chat_id": "dcfa5a7c-7cc4-4c89-b6c0-80325604f9f4",
                },
            ),
            ChatNotFoundError,
            ("chat_not_found",),
        ),
    ],
)
async def test__unpin_message__error_response(
    response_status: int,
    response_json: dict[str, Any],
    expected_exc: Type[Exception],
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
            await bot.unpin_message(
                bot_id=bot_id,
                chat_id=UUID("054af49e-5e18-4dca-ad73-4f96b6de63fa"),
            )

    # - Assert -
    for fragment in expected_fragments:
        assert fragment in str(exc.value)
    assert endpoint.called


async def test__unpin_message__succeed(
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
        ok_payload("message_unpinned"),
        HTTPStatus.OK,
    )

    # - Act -
    async with bot_factory() as bot:
        await bot.unpin_message(
            bot_id=bot_id,
            chat_id=UUID("054af49e-5e18-4dca-ad73-4f96b6de63fa"),
        )

    # - Assert -
    assert endpoint.called
