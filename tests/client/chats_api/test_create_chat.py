from http import HTTPStatus
from uuid import UUID

import httpx
import pytest
from respx.router import MockRouter

from botx import (
    Bot,
    BotAccountWithSecret,
    ChatCreationError,
    ChatCreationProhibitedError,
    ChatTypes,
    HandlerCollector,
    lifespan_wrapper,
)

pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.mock_authorization,
    pytest.mark.usefixtures("respx_mock"),
]


async def test__create_chat__bot_have_no_permissions_raised(
    respx_mock: MockRouter,
    host: str,
    bot_id: UUID,
    bot_account: BotAccountWithSecret,
) -> None:
    # - Arrange -
    endpoint = respx_mock.post(
        f"https://{host}/api/v3/botx/chats/create",
        headers={"Authorization": "Bearer token", "Content-Type": "application/json"},
        json={
            "name": "Test chat name",
            "description": None,
            "chat_type": "group_chat",
            "members": [],
        },
    ).mock(
        return_value=httpx.Response(
            HTTPStatus.FORBIDDEN,
            json={
                "status": "error",
                "reason": "chat_creation_is_prohibited",
                "errors": ["This bot is not allowed to create chats"],
                "error_data": {
                    "bot_id": "a465f0f3-1354-491c-8f11-f400164295cb",
                },
            },
        ),
    )

    built_bot = Bot(collectors=[HandlerCollector()], bot_accounts=[bot_account])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        with pytest.raises(ChatCreationProhibitedError) as exc:
            await bot.create_chat(
                bot_id=bot_id,
                name="Test chat name",
                chat_type=ChatTypes.GROUP_CHAT,
                huids=[],
            )

    # - Assert -
    assert endpoint.called
    assert "chat_creation_is_prohibited" in str(exc.value)


async def test__create_chat__botx_error_raised(
    respx_mock: MockRouter,
    host: str,
    bot_id: UUID,
    bot_account: BotAccountWithSecret,
) -> None:
    # - Arrange -
    endpoint = respx_mock.post(
        f"https://{host}/api/v3/botx/chats/create",
        headers={"Authorization": "Bearer token", "Content-Type": "application/json"},
        json={
            "name": "Test chat name",
            "description": None,
            "chat_type": "group_chat",
            "members": [],
        },
    ).mock(
        return_value=httpx.Response(
            HTTPStatus.UNPROCESSABLE_ENTITY,
            json={
                "status": "error",
                "reason": "|specified reason|",
                "errors": ["|specified errors|"],
                "error_data": {},
            },
        ),
    )

    built_bot = Bot(collectors=[HandlerCollector()], bot_accounts=[bot_account])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        with pytest.raises(ChatCreationError) as exc:
            await bot.create_chat(
                bot_id=bot_id,
                name="Test chat name",
                chat_type=ChatTypes.GROUP_CHAT,
                huids=[],
            )

    # - Assert -
    assert endpoint.called
    assert "specified reason" in str(exc.value)


async def test__create_chat__maximum_filled_succeed(
    respx_mock: MockRouter,
    host: str,
    bot_id: UUID,
    bot_account: BotAccountWithSecret,
) -> None:
    # - Arrange -
    endpoint = respx_mock.post(
        f"https://{host}/api/v3/botx/chats/create",
        headers={"Authorization": "Bearer token", "Content-Type": "application/json"},
        json={
            "name": "Test chat name",
            "description": "Test description",
            "chat_type": "group_chat",
            "members": ["2fc83441-366a-49ba-81fc-6c39f065bb58"],
            "shared_history": True,
        },
    ).mock(
        return_value=httpx.Response(
            HTTPStatus.OK,
            json={
                "status": "ok",
                "result": {"chat_id": "054af49e-5e18-4dca-ad73-4f96b6de63fa"},
            },
        ),
    )

    built_bot = Bot(collectors=[HandlerCollector()], bot_accounts=[bot_account])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        created_chat_id = await bot.create_chat(
            bot_id=bot_id,
            name="Test chat name",
            chat_type=ChatTypes.GROUP_CHAT,
            huids=[UUID("2fc83441-366a-49ba-81fc-6c39f065bb58")],
            description="Test description",
            shared_history=True,
        )

    # - Assert -
    assert created_chat_id == UUID("054af49e-5e18-4dca-ad73-4f96b6de63fa")
    assert endpoint.called
