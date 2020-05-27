import threading

import pytest

from botx import Collector

pytest_plugins = ("tests.test_collecting.fixtures",)
pytestmark = pytest.mark.asyncio


async def test_execution_when_full_match(message, build_handler):
    event = threading.Event()
    message.command.body = "/command"

    collector = Collector()
    collector.add_handler(build_handler(event), body=message.command.body)

    await collector.handle_message(message)

    assert event.is_set()


async def test_executing_handler_when_partial_match(message, build_handler):
    event = threading.Event()
    message.command.body = "/command with arguments"

    collector = Collector()
    collector.add_handler(build_handler(event), body=message.command.command)

    await collector.handle_message(message)

    assert event.is_set()
