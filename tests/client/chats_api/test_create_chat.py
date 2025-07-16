from http import HTTPStatus
from uuid import UUID

import httpx
import pytest
from respx.router import MockRouter

from pybotx import (
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
            "avatar": None,
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
            "avatar": None,
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
            "avatar": None,
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


def test__create_chat_payload__invalid_avatar_non_data_url_error() -> None:
    """Test that BotXAPICreateChatRequestPayload validator raises ValueError for non-data URL avatar."""
    from pybotx.client.chats_api.create_chat import BotXAPICreateChatRequestPayload

    # Test the validator directly since UnverifiedPayloadBaseModel bypasses validation
    # The validator is a classmethod that expects (cls, value)
    with pytest.raises(ValueError, match="Avatar must be a data URL \\(RFC2397\\)"):
        BotXAPICreateChatRequestPayload._validate_avatar("invalid-url")


def test__create_chat_payload__invalid_avatar_bad_rfc2397_format_error() -> None:
    """Test that BotXAPICreateChatRequestPayload validator raises ValueError for invalid RFC2397 format."""
    from pybotx.client.chats_api.create_chat import BotXAPICreateChatRequestPayload

    # Test the validator directly since UnverifiedPayloadBaseModel bypasses validation
    with pytest.raises(ValueError, match="Invalid data URL format"):
        BotXAPICreateChatRequestPayload._validate_avatar("data:invalid-format")


def test__create_chat_payload__avatar_validator_with_none() -> None:
    """Test that BotXAPICreateChatRequestPayload avatar validator handles None correctly."""
    from pybotx.client.chats_api.create_chat import BotXAPICreateChatRequestPayload

    # Test the validator directly with None value
    result = BotXAPICreateChatRequestPayload._validate_avatar(None)
    assert result is None


def test__create_chat_payload__avatar_validator_with_valid_data_url() -> None:
    """Test that BotXAPICreateChatRequestPayload avatar validator handles valid data URL correctly."""
    from pybotx.client.chats_api.create_chat import BotXAPICreateChatRequestPayload

    valid_avatar = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="
    result = BotXAPICreateChatRequestPayload._validate_avatar(valid_avatar)
    assert result == valid_avatar


def test__create_chat_payload__convert_chat_type_validator() -> None:
    """Test that BotXAPICreateChatRequestPayload converts ChatTypes to APIChatTypes."""
    from pybotx.client.chats_api.create_chat import BotXAPICreateChatRequestPayload
    from pybotx.models.enums import ChatTypes, APIChatTypes

    # Test with ChatTypes enum
    values = {"chat_type": ChatTypes.GROUP_CHAT}
    result = BotXAPICreateChatRequestPayload._convert_chat_type(values)  # type: ignore[operator]
    assert result["chat_type"] == APIChatTypes.GROUP_CHAT

    # Test with non-ChatTypes value (should remain unchanged)
    values = {"chat_type": APIChatTypes.CHAT}  # type: ignore[dict-item]
    result = BotXAPICreateChatRequestPayload._convert_chat_type(values)  # type: ignore[operator]
    assert result["chat_type"] == APIChatTypes.CHAT

    # Test with missing chat_type key
    values = {"name": "test"}  # type: ignore[dict-item]
    result = BotXAPICreateChatRequestPayload._convert_chat_type(values)  # type: ignore[operator]
    assert result == {"name": "test"}


async def test__create_chat__with_valid_avatar_succeed(
    respx_mock: MockRouter,
    host: str,
    bot_id: UUID,
    bot_account: BotAccountWithSecret,
) -> None:
    # - Arrange -
    valid_avatar = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="

    endpoint = respx_mock.post(
        f"https://{host}/api/v3/botx/chats/create",
        headers={"Authorization": "Bearer token", "Content-Type": "application/json"},
        json={
            "name": "Test chat name",
            "description": None,
            "chat_type": "group_chat",
            "members": [],
            "avatar": valid_avatar,
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
            huids=[],
            avatar=valid_avatar,
        )

    # - Assert -
    assert created_chat_id == UUID("054af49e-5e18-4dca-ad73-4f96b6de63fa")
    assert endpoint.called
