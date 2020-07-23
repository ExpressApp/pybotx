import threading
from typing import Any

import pytest

from botx import Message
from botx.middlewares.ns import NextStepMiddleware, register_next_step_handler

pytestmark = pytest.mark.asyncio


@pytest.fixture()
def build_handler_to_store_arguments():
    def factory(next_handler_name: str, event: threading.Event, **ns_args: Any):
        def decorator(message: Message):
            event.set()
            register_next_step_handler(message, next_handler_name, **ns_args)

        return decorator

    return factory


@pytest.fixture()
def build_handler_to_save_message_in_storage(storage):
    def factory(event: threading.Event):
        def decorator(message: Message):
            event.set()
            storage.state = message.state

        return decorator

    return factory


async def test_setting_args_into_message_state(
    bot,
    incoming_message,
    client,
    build_handler_to_store_arguments,
    build_handler_to_save_message_in_storage,
    storage,
):
    event1 = threading.Event()
    event2 = threading.Event()

    bot.default(
        handler=build_handler_to_store_arguments(
            "ns_handler", event1, arg1=1, arg2="2", arg3=True,
        ),
    )

    ns_handler = build_handler_to_save_message_in_storage(event2)

    bot.add_middleware(
        NextStepMiddleware, bot=bot, functions={"ns_handler": ns_handler},
    )

    await client.send_command(incoming_message)
    assert event1.is_set()

    await client.send_command(incoming_message)
    assert event2.is_set()

    assert storage.state.arg1 == 1
    assert storage.state.arg2 == "2"
    assert storage.state.arg3
