import pytest

from pybotx import (
    Bot,
    HandlerCollector,
    UnknownSystemEventError,
    UnsupportedBotAPIVersionError,
    lifespan_wrapper,
)

pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.mock_authorization,
    pytest.mark.usefixtures("respx_mock"),
]


async def test__async_execute_raw_bot_command__invalid_payload_value_error_raised() -> None:
    # - Arrange -
    payload = {"invalid": "command"}
    built_bot = Bot(collectors=[HandlerCollector()], bot_accounts=[])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        with pytest.raises(ValueError) as exc:
            bot.async_execute_raw_bot_command(payload)

    # - Assert -
    assert "validation" in str(exc.value)


async def test__async_execute_raw_bot_command__unsupported_bot_api_version_error_raised() -> None:
    # - Arrange -
    payload = {"proto_version": "3"}
    built_bot = Bot(collectors=[HandlerCollector()], bot_accounts=[])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        with pytest.raises(UnsupportedBotAPIVersionError) as exc:
            bot.async_execute_raw_bot_command(payload)

    # - Assert -
    assert "Unsupported" in str(exc.value)
    assert "expected `4`" in str(exc.value)


async def test__async_execute_raw_bot_command__unknown_system_event() -> None:
    # - Arrange -
    payload = {
        "async_files": [],
        "attachments": [],
        "bot_id": "24348246-6791-4ac0-9d86-b948cd6a0e46",
        "command": {
            "body": "system:baz",
            "command_type": "system",
            "data": {"foo": "bar"},
            "metadata": {},
        },
        "entities": [],
        "from": {
            "ad_domain": None,
            "ad_login": None,
            "app_version": None,
            "chat_type": None,
            "device": None,
            "device_meta": {},
            "device_software": None,
            "group_chat_id": None,
            "host": "cts.example.com",
            "is_admin": None,
            "is_creator": None,
            "locale": "en",
            "manufacturer": None,
            "platform": None,
            "platform_package_id": None,
            "user_huid": None,
            "username": None,
        },
        "proto_version": 4,
        "source_sync_id": None,
        "sync_id": "2b97fa97-4236-5ebf-b299-a618bf8c3fef",
    }
    built_bot = Bot(collectors=[HandlerCollector()], bot_accounts=[])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        with pytest.raises(UnknownSystemEventError) as exc:
            bot.async_execute_raw_bot_command(payload)

    # - Assert -
    assert "Unknown system event" in str(exc.value)
    assert "system:baz" in str(exc.value)
