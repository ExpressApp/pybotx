from http import HTTPStatus
from typing import Any, Type
from uuid import UUID

import pytest
from respx.router import MockRouter

from pybotx import (
    BotIsNotChatMemberError,
    ChatNotFoundError,
    FinalRecipientsListEmptyError,
    StealthModeDisabledError,
)
from pybotx.client.exceptions.http import InvalidBotXResponsePayloadError
from tests.testkit import BotXRequest, error_payload, mock_botx, ok_payload

pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.mock_authorization,
    pytest.mark.usefixtures("respx_mock"),
]

ENDPOINT = "/api/v4/botx/notifications/direct/sync"

REQUEST = BotXRequest(
    method="POST",
    path=ENDPOINT,
    json={
        "group_chat_id": "054af49e-5e18-4dca-ad73-4f96b6de63fa",
        "notification": {"status": "ok", "body": "Hi!"},
    },
)


async def test__send_message_sync__succeed(
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
        ok_payload({"sync_id": "21a9ec9e-f21f-4406-ac44-1a78d2ccf9e3"}),
        HTTPStatus.OK,
    )

    # - Act -
    async with bot_factory() as bot:
        sync_id = await bot.send_message_sync(
            body="Hi!",
            bot_id=bot_id,
            chat_id=UUID("054af49e-5e18-4dca-ad73-4f96b6de63fa"),
        )

    # - Assert -
    assert sync_id == UUID("21a9ec9e-f21f-4406-ac44-1a78d2ccf9e3")
    assert endpoint.called


@pytest.mark.parametrize(
    ("reason", "exc_type"),
    [
        ("chat_not_found", ChatNotFoundError),
        ("bot_is_not_a_chat_member", BotIsNotChatMemberError),
        ("event_recipients_list_is_empty", FinalRecipientsListEmptyError),
        ("stealth_mode_disabled", StealthModeDisabledError),
    ],
)
async def test__send_message_sync__known_error_reason_raised(
    reason: str,
    exc_type: Type[Exception],
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
        error_payload(
            reason,
            error_data={
                "group_chat_id": "054af49e-5e18-4dca-ad73-4f96b6de63fa",
            },
        ),
        HTTPStatus.OK,
    )

    # - Act -
    async with bot_factory() as bot:
        with pytest.raises(exc_type):
            await bot.send_message_sync(
                body="Hi!",
                bot_id=bot_id,
                chat_id=UUID("054af49e-5e18-4dca-ad73-4f96b6de63fa"),
            )

    # - Assert -
    assert endpoint.called


async def test__send_message_sync__unknown_error_reason_raised(
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
        error_payload("unknown_reason"),
        HTTPStatus.OK,
    )

    # - Act -
    async with bot_factory() as bot:
        with pytest.raises(InvalidBotXResponsePayloadError):
            await bot.send_message_sync(
                body="Hi!",
                bot_id=bot_id,
                chat_id=UUID("054af49e-5e18-4dca-ad73-4f96b6de63fa"),
            )

    # - Assert -
    assert endpoint.called
