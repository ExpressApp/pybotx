import threading

import pytest

from botx import TestClient

pytestmark = pytest.mark.asyncio


async def test_handling_exception_with_custom_catcher(
    bot,
    incoming_message,
    client,
    build_exception_catcher,
    build_failed_handler,
    storage,
):
    exc_for_raising = Exception("exception from handler")

    cather_event = threading.Event()
    handler_event = threading.Event()

    bot.add_exception_handler(Exception, build_exception_catcher(cather_event))
    bot.default(build_failed_handler(exc_for_raising, handler_event))

    await client.send_command(incoming_message)

    assert cather_event.is_set()
    assert handler_event.is_set()
    assert storage.exception == exc_for_raising
    assert storage.message.incoming_message == incoming_message


async def test_handling_from_nearest_mro_handler(
    bot,
    incoming_message,
    client,
    build_exception_catcher,
    build_failed_handler,
    storage,
):
    exc_for_raising = UnicodeError("exception from handler")

    exception_catcher_event = threading.Event()
    value_error_catcher_event = threading.Event()
    handler_event = threading.Event()

    bot.add_exception_handler(
        Exception,
        build_exception_catcher(exception_catcher_event),
    )
    bot.add_exception_handler(
        Exception,
        build_exception_catcher(value_error_catcher_event),
    )
    bot.default(handler=build_failed_handler(exc_for_raising, handler_event))

    await client.send_command(incoming_message)

    assert not exception_catcher_event.is_set()
    assert value_error_catcher_event.is_set()
    assert handler_event.is_set()
    assert storage.exception == exc_for_raising
    assert storage.message.incoming_message == incoming_message


async def test_logging_exception_if_was_not_found(
    bot,
    incoming_message,
    loguru_caplog,
    build_failed_handler,
) -> None:
    event = threading.Event()
    bot.default(build_failed_handler(ValueError, event))

    with TestClient(bot, suppress_errors=True) as client:
        await client.send_command(incoming_message)

    assert event.is_set()
    assert "uncaught ValueError exception" in loguru_caplog.text
