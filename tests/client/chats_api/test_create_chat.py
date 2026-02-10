from http import HTTPStatus
from typing import Any
from collections.abc import Sequence
from uuid import UUID

import pytest
from respx.router import MockRouter

from pybotx import ChatCreationError, ChatCreationProhibitedError, ChatTypes
from pybotx.testkit import BotXRequest, error_payload, mock_botx, ok_payload

pytestmark = [
    pytest.mark.mock_authorization,
    pytest.mark.usefixtures("respx_mock"),
]

ENDPOINT = "/api/v3/botx/chats/create"

REQUEST_BASE = BotXRequest(
    method="POST",
    path=ENDPOINT,
    json={
        "name": "Test chat name",
        "description": None,
        "chat_type": "group_chat",
        "members": [],
        "avatar": None,
    },
)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("response_status", "response_json", "expected_exc", "expected_fragments"),
    [
        (
            HTTPStatus.FORBIDDEN,
            error_payload(
                "chat_creation_is_prohibited",
                errors=["This bot is not allowed to create chats"],
                error_data={
                    "bot_id": "a465f0f3-1354-491c-8f11-f400164295cb",
                },
            ),
            ChatCreationProhibitedError,
            ("chat_creation_is_prohibited",),
        ),
        (
            HTTPStatus.UNPROCESSABLE_ENTITY,
            error_payload(
                "|specified reason|",
                errors=["|specified errors|"],
            ),
            ChatCreationError,
            ("specified reason",),
        ),
    ],
)
async def test__create_chat__error_response(
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
    endpoint = mock_botx(respx_mock, host, REQUEST_BASE, response_json, response_status)

    # - Act -
    async with bot_factory() as bot:
        with pytest.raises(expected_exc) as exc:
            await bot.create_chat(
                bot_id=bot_id,
                name="Test chat name",
                chat_type=ChatTypes.GROUP_CHAT,
                huids=[],
            )

    # - Assert -
    for fragment in expected_fragments:
        assert fragment in str(exc.value)
    assert endpoint.called


@pytest.mark.asyncio
async def test__create_chat__maximum_filled_succeed(
    respx_mock: MockRouter,
    host: str,
    bot_id: UUID,
    bot_factory: Any,
) -> None:
    # - Arrange -
    request = BotXRequest(
        method="POST",
        path=ENDPOINT,
        json={
            "name": "Test chat name",
            "description": "Test description",
            "chat_type": "group_chat",
            "members": ["2fc83441-366a-49ba-81fc-6c39f065bb58"],
            "shared_history": True,
            "avatar": None,
        },
    )
    endpoint = mock_botx(
        respx_mock,
        host,
        request,
        ok_payload({"chat_id": "054af49e-5e18-4dca-ad73-4f96b6de63fa"}),
        HTTPStatus.OK,
    )

    # - Act -
    async with bot_factory() as bot:
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


@pytest.mark.asyncio
async def test__create_chat__with_valid_avatar_succeed(
    respx_mock: MockRouter,
    host: str,
    bot_id: UUID,
    bot_factory: Any,
) -> None:
    # - Arrange -
    valid_avatar = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="

    request = BotXRequest(
        method="POST",
        path=ENDPOINT,
        json={
            "name": "Test chat name",
            "description": None,
            "chat_type": "group_chat",
            "members": [],
            "avatar": valid_avatar,
        },
    )
    endpoint = mock_botx(
        respx_mock,
        host,
        request,
        ok_payload({"chat_id": "054af49e-5e18-4dca-ad73-4f96b6de63fa"}),
        HTTPStatus.OK,
    )

    # - Act -
    async with bot_factory() as bot:
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


def test__create_chat_payload__invalid_avatar_non_data_url_error() -> None:
    """Test that BotXAPICreateChatRequestPayload validator raises InvalidAvatarDataError for non-data URL avatar."""
    from pybotx.infrastructure.client.chats_api.create_chat import BotXAPICreateChatRequestPayload
    from pybotx import InvalidAvatarDataError

    # Test the validator directly since UnverifiedPayloadBaseModel bypasses validation
    # The validator is a classmethod that expects (cls, value)
    with pytest.raises(InvalidAvatarDataError, match="Avatar must be a data URL \\(RFC2397\\)"):
        BotXAPICreateChatRequestPayload._validate_avatar("invalid-url")


def test__create_chat_payload__invalid_avatar_bad_rfc2397_format_error() -> None:
    """Test that BotXAPICreateChatRequestPayload validator raises InvalidAvatarDataError for invalid RFC2397 format."""
    from pybotx.infrastructure.client.chats_api.create_chat import BotXAPICreateChatRequestPayload
    from pybotx import InvalidAvatarDataError

    # Test the validator directly since UnverifiedPayloadBaseModel bypasses validation
    with pytest.raises(InvalidAvatarDataError, match="Invalid data URL format"):
        BotXAPICreateChatRequestPayload._validate_avatar("data:invalid-format")


def test__create_chat_payload__avatar_validator_with_none() -> None:
    """Test that BotXAPICreateChatRequestPayload avatar validator handles None correctly."""
    from pybotx.infrastructure.client.chats_api.create_chat import BotXAPICreateChatRequestPayload

    # Test the validator directly with None value
    result = BotXAPICreateChatRequestPayload._validate_avatar(None)
    assert result is None


def test__create_chat_payload__avatar_validator_with_valid_data_url() -> None:
    """Test that BotXAPICreateChatRequestPayload avatar validator handles valid data URL correctly."""
    from pybotx.infrastructure.client.chats_api.create_chat import BotXAPICreateChatRequestPayload

    valid_avatar = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="
    result = BotXAPICreateChatRequestPayload._validate_avatar(valid_avatar)
    assert result == valid_avatar


def test__create_chat_payload__convert_chat_type_validator() -> None:
    """Test that BotXAPICreateChatRequestPayload converts ChatTypes to APIChatTypes."""
    from pybotx.infrastructure.client.chats_api.create_chat import BotXAPICreateChatRequestPayload
    from pybotx.domain.models.enums import ChatTypes
    from pybotx.infrastructure.contracts.enums import APIChatTypes

    # Test with ChatTypes enum
    values = {"chat_type": ChatTypes.GROUP_CHAT}
    result = BotXAPICreateChatRequestPayload._convert_chat_type(values)  # type: ignore[operator]
    assert result["chat_type"] == APIChatTypes.GROUP_CHAT

    # Test with APIChatTypes value (should remain unchanged)
    values = {"chat_type": APIChatTypes.CHAT}  # type: ignore[dict-item]
    result = BotXAPICreateChatRequestPayload._convert_chat_type(values)  # type: ignore[operator]
    assert result["chat_type"] == APIChatTypes.CHAT

    # Test with missing chat_type key
    values = {"name": "test"}  # type: ignore[dict-item]
    result = BotXAPICreateChatRequestPayload._convert_chat_type(values)  # type: ignore[operator]
    assert result == {"name": "test"}


def test__create_chat_payload__serialize_chat_type_from_domain() -> None:
    """Test that chat_type serialization converts ChatTypes to API value."""
    from pybotx.infrastructure.client.chats_api.create_chat import BotXAPICreateChatRequestPayload
    from pybotx.domain.models.enums import ChatTypes
    from pybotx.infrastructure.contracts.enums import APIChatTypes
    from pybotx.domain.missing import Undefined

    payload = BotXAPICreateChatRequestPayload(
        name="Test chat name",
        description=None,
        chat_type=ChatTypes.PERSONAL_CHAT,
        members=[],
        shared_history=Undefined,
        avatar=None,
    )

    dumped = payload.model_dump(mode="json", exclude={"shared_history"})
    assert dumped["chat_type"] == "chat"

    payload_api = BotXAPICreateChatRequestPayload(
        name="Test chat name",
        description=None,
        chat_type=APIChatTypes.GROUP_CHAT,
        members=[],
        shared_history=Undefined,
        avatar=None,
    )

    dumped_api = payload_api.model_dump(mode="json", exclude={"shared_history"})
    assert dumped_api["chat_type"] == "group_chat"
