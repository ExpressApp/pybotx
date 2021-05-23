import threading

import pytest

from botx.middlewares.ns import NextStepMiddleware

pytestmark = pytest.mark.asyncio
pytest_plugins = ("tests.test_middlewares.test_ns_middleware.fixtures",)


async def test_error_for_ns_for_unregistered_handler(
    bot,
    client,
    incoming_message,
    build_handler_to_start_chain,
):
    event = threading.Event()

    bot.default(handler=build_handler_to_start_chain("unknown_handler_name", event))

    bot.add_middleware(NextStepMiddleware, bot=bot, functions={})

    with pytest.raises(ValueError):
        await client.send_command(incoming_message)

    assert event.is_set()


async def test_error_for_message_without_huid(
    bot,
    incoming_message,
    client,
    chat_created_message,
    build_handler_to_start_chain,
    build_handler_for_collector,
):
    event = threading.Event()
    bot.chat_created(build_handler_to_start_chain("ns_handler", event))

    bot.add_middleware(
        NextStepMiddleware,
        bot=bot,
        functions={build_handler_for_collector("ns_handler")},
    )

    with pytest.raises(ValueError):
        await client.send_command(chat_created_message)

    assert event.is_set()
