from http import HTTPStatus
from uuid import UUID

import httpx
import pytest
from respx.router import MockRouter

from botx import (
    Bot,
    BotAccountWithSecret,
    ChatNotFoundError,
    HandlerCollector,
    PermissionDeniedError,
    lifespan_wrapper,
)

pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.mock_authorization,
    pytest.mark.usefixtures("respx_mock"),
]


async def test__pin_message__permission_denied_error_raised(
    respx_mock: MockRouter,
    host: str,
    bot_id: UUID,
    bot_account: BotAccountWithSecret,
) -> None:
    # - Arrange -
    endpoint = respx_mock.post(
        f"https://{host}/api/v3/botx/chats/pin_message",
        headers={"Authorization": "Bearer token", "Content-Type": "application/json"},
        json={
            "chat_id": "054af49e-5e18-4dca-ad73-4f96b6de63fa",
            "sync_id": "21a9ec9e-f21f-4406-ac44-1a78d2ccf9e3",
        },
    ).mock(
        return_value=httpx.Response(
            HTTPStatus.FORBIDDEN,
            json={
                "error_data": {
                    "bot_id": "f9e1c958-bf81-564e-bff2-a2943869af15",
                    "error_description": "Bot doesn't have permission for this operation in current chat",
                    "group_chat_id": "5680c26a-07a5-5b40-a6ff-f5e7e68fed25",
                },
                "errors": [],
                "reason": "no_permission_for_operation",
                "status": "error",
            },
        ),
    )

    built_bot = Bot(collectors=[HandlerCollector()], bot_accounts=[bot_account])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        with pytest.raises(PermissionDeniedError) as exc:
            await bot.pin_message(
                bot_id=bot_id,
                chat_id=UUID("054af49e-5e18-4dca-ad73-4f96b6de63fa"),
                sync_id=UUID("21a9ec9e-f21f-4406-ac44-1a78d2ccf9e3"),
            )

    # - Assert -
    assert "no_permission_for_operation" in str(exc.value)
    assert endpoint.called


async def test__pin_message__chat_not_found_error_raised(
    respx_mock: MockRouter,
    host: str,
    bot_id: UUID,
    bot_account: BotAccountWithSecret,
) -> None:
    # - Arrange -
    endpoint = respx_mock.post(
        f"https://{host}/api/v3/botx/chats/pin_message",
        headers={"Authorization": "Bearer token", "Content-Type": "application/json"},
        json={
            "chat_id": "054af49e-5e18-4dca-ad73-4f96b6de63fa",
            "sync_id": "21a9ec9e-f21f-4406-ac44-1a78d2ccf9e3",
        },
    ).mock(
        return_value=httpx.Response(
            HTTPStatus.NOT_FOUND,
            json={
                "status": "error",
                "reason": "chat_not_found",
                "errors": [],
                "error_data": {
                    "error_description": "Chat with specified id not found",
                    "group_chat_id": "dcfa5a7c-7cc4-4c89-b6c0-80325604f9f4",
                },
            },
        ),
    )

    built_bot = Bot(collectors=[HandlerCollector()], bot_accounts=[bot_account])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        with pytest.raises(ChatNotFoundError) as exc:
            await bot.pin_message(
                bot_id=bot_id,
                chat_id=UUID("054af49e-5e18-4dca-ad73-4f96b6de63fa"),
                sync_id=UUID("21a9ec9e-f21f-4406-ac44-1a78d2ccf9e3"),
            )

    # - Assert -
    assert "chat_not_found" in str(exc.value)
    assert endpoint.called


async def test__pin_message__succeed(
    respx_mock: MockRouter,
    host: str,
    bot_id: UUID,
    bot_account: BotAccountWithSecret,
) -> None:
    # - Arrange -
    endpoint = respx_mock.post(
        f"https://{host}/api/v3/botx/chats/pin_message",
        headers={"Authorization": "Bearer token", "Content-Type": "application/json"},
        json={
            "chat_id": "054af49e-5e18-4dca-ad73-4f96b6de63fa",
            "sync_id": "21a9ec9e-f21f-4406-ac44-1a78d2ccf9e3",
        },
    ).mock(
        return_value=httpx.Response(
            HTTPStatus.OK,
            json={"status": "ok", "result": "message_pinned"},
        ),
    )

    built_bot = Bot(collectors=[HandlerCollector()], bot_accounts=[bot_account])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        await bot.pin_message(
            bot_id=bot_id,
            chat_id=UUID("054af49e-5e18-4dca-ad73-4f96b6de63fa"),
            sync_id=UUID("21a9ec9e-f21f-4406-ac44-1a78d2ccf9e3"),
        )

    # - Assert -
    assert endpoint.called
