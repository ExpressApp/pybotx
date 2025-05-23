import json
import logging
from typing import Any, Callable, Dict

import pytest

from pybotx import (
    Bot,
    BotAccountWithSecret,
    HandlerCollector,
    RequestHeadersNotProvidedError,
    UnknownSystemEventError,
    UnsupportedBotAPIVersionError,
    lifespan_wrapper,
)

pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.mock_authorization,
    pytest.mark.usefixtures("respx_mock"),
]


async def test__async_execute_raw_bot_command__invalid_payload_value_error_raised() -> (
    None
):
    # - Arrange -
    payload = {"invalid": "command"}
    built_bot = Bot(collectors=[HandlerCollector()], bot_accounts=[])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        with pytest.raises(ValueError) as exc:
            bot.async_execute_raw_bot_command(payload, verify_request=False)

    # - Assert -
    assert "validation" in str(exc.value)


async def test__async_execute_raw_bot_command__unsupported_bot_api_version_error_raised() -> (
    None
):
    # - Arrange -
    payload = {"proto_version": "3"}
    built_bot = Bot(collectors=[HandlerCollector()], bot_accounts=[])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        with pytest.raises(UnsupportedBotAPIVersionError) as exc:
            bot.async_execute_raw_bot_command(payload, verify_request=False)

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
            bot.async_execute_raw_bot_command(payload, verify_request=False)

    # - Assert -
    assert "Unknown system event" in str(exc.value)
    assert "system:baz" in str(exc.value)


async def test__async_execute_raw_bot_command__logging_incoming_request(
    bot_account: BotAccountWithSecret,
    loguru_caplog: pytest.LogCaptureFixture,
    api_incoming_message_factory: Callable[..., Dict[str, Any]],
    mock_authorization: None,
) -> None:
    # - Arrange -
    payload = api_incoming_message_factory(bot_id=bot_account.id)
    log_message = "Got command: {command}".format(
        command=json.dumps(payload, sort_keys=True, indent=4, ensure_ascii=False),
    )
    built_bot = Bot(collectors=[HandlerCollector()], bot_accounts=[bot_account])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        with loguru_caplog.at_level(logging.DEBUG):
            bot.async_execute_raw_bot_command(payload, verify_request=False)

    # - Assert -
    assert log_message in loguru_caplog.messages


async def test__async_execute_raw_bot_command__not_logging_incoming_request(
    bot_account: BotAccountWithSecret,
    loguru_caplog: pytest.LogCaptureFixture,
    api_incoming_message_factory: Callable[..., Dict[str, Any]],
    mock_authorization: None,
) -> None:
    # - Arrange -
    payload = api_incoming_message_factory(bot_id=bot_account.id)
    log_message = "Got command: {command}".format(
        command=json.dumps(payload, sort_keys=True, indent=4, ensure_ascii=False),
    )
    built_bot = Bot(collectors=[HandlerCollector()], bot_accounts=[bot_account])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        with loguru_caplog.at_level(logging.DEBUG):
            bot.async_execute_raw_bot_command(
                payload,
                verify_request=False,
                logging_command=False,
            )

    # - Assert -
    assert log_message not in loguru_caplog.messages


async def test__sync_execute_raw_smartapp_event__logging_incoming_request(
    bot_account: BotAccountWithSecret,
    loguru_caplog: pytest.LogCaptureFixture,
    api_sync_smartapp_event_factory: Callable[..., Dict[str, Any]],
    collector_with_sync_smartapp_event_handler: HandlerCollector,
) -> None:
    # - Arrange -
    payload = api_sync_smartapp_event_factory(bot_id=bot_account.id)
    log_message = "Got sync smartapp event: {command}".format(
        command=json.dumps(payload, sort_keys=True, indent=4, ensure_ascii=False),
    )
    built_bot = Bot(
        collectors=[collector_with_sync_smartapp_event_handler],
        bot_accounts=[bot_account],
    )

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        with loguru_caplog.at_level(logging.DEBUG):
            await bot.sync_execute_raw_smartapp_event(payload, verify_request=False)

    # - Assert -
    assert log_message in loguru_caplog.messages


async def test__sync_execute_raw_smartapp_event__not_logging_incoming_request(
    bot_account: BotAccountWithSecret,
    loguru_caplog: pytest.LogCaptureFixture,
    api_sync_smartapp_event_factory: Callable[..., Dict[str, Any]],
    collector_with_sync_smartapp_event_handler: HandlerCollector,
) -> None:
    # - Arrange -
    payload = api_sync_smartapp_event_factory(bot_id=bot_account.id)
    log_message = "Got sync smartapp event: {command}".format(
        command=json.dumps(payload, sort_keys=True, indent=4, ensure_ascii=False),
    )
    built_bot = Bot(
        collectors=[collector_with_sync_smartapp_event_handler],
        bot_accounts=[bot_account],
    )

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        with loguru_caplog.at_level(logging.DEBUG):
            await bot.sync_execute_raw_smartapp_event(
                payload,
                verify_request=False,
                logging_command=False,
            )

    # - Assert -
    assert log_message not in loguru_caplog.messages


async def test__sync_execute_raw_smartapp_event__headers_not_provided(
    bot_account: BotAccountWithSecret,
    api_sync_smartapp_event_factory: Callable[..., Dict[str, Any]],
    collector_with_sync_smartapp_event_handler: HandlerCollector,
) -> None:
    # - Arrange -
    payload = api_sync_smartapp_event_factory(bot_id=bot_account.id)
    built_bot = Bot(
        collectors=[collector_with_sync_smartapp_event_handler],
        bot_accounts=[bot_account],
    )

    # - Act and Assert-
    async with lifespan_wrapper(built_bot) as bot:
        with pytest.raises(RequestHeadersNotProvidedError):
            await bot.sync_execute_raw_smartapp_event(payload, verify_request=True)


async def test__sync_execute_raw_smartapp_event__request_verified(
    bot_account: BotAccountWithSecret,
    api_sync_smartapp_event_factory: Callable[..., Dict[str, Any]],
    collector_with_sync_smartapp_event_handler: HandlerCollector,
    authorization_header: Dict[str, str],
) -> None:
    # - Arrange -
    payload = api_sync_smartapp_event_factory(bot_id=bot_account.id)
    built_bot = Bot(
        collectors=[collector_with_sync_smartapp_event_handler],
        bot_accounts=[bot_account],
    )

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        response = await bot.sync_execute_raw_smartapp_event(
            payload,
            verify_request=True,
            request_headers=authorization_header,
        )

    assert response


async def test__sync_execute_raw_smartapp_event__incorrect_payload(
    bot_account: BotAccountWithSecret,
    collector_with_sync_smartapp_event_handler: HandlerCollector,
) -> None:
    # - Arrange -
    payload = {"incorrect": "payload"}
    built_bot = Bot(
        collectors=[collector_with_sync_smartapp_event_handler],
        bot_accounts=[bot_account],
    )

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        with pytest.raises(ValueError):
            await bot.sync_execute_raw_smartapp_event(
                payload,
                verify_request=False,
                logging_command=False,
            )
