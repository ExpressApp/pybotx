import threading

import pytest

from botx import Depends

pytestmark = pytest.mark.asyncio


async def test_that_dependency_can_be_overriden(
    bot,
    client,
    incoming_message,
    build_handler,
):
    handler_event = threading.Event()
    original_dependency_event = threading.Event()
    fake_dependency_event = threading.Event()

    dependency = build_handler(original_dependency_event)
    bot.default(build_handler(handler_event), dependencies=[Depends(dependency)])

    bot.dependency_overrides[dependency] = build_handler(fake_dependency_event)

    await client.send_command(incoming_message)

    assert handler_event.is_set()
    assert not original_dependency_event.is_set()
    assert fake_dependency_event.is_set()


async def test_bot_is_used_as_default_provider(
    bot,
    client,
    incoming_message,
    build_handler,
):
    handler_event = threading.Event()
    original_dependency_event = threading.Event()
    fake_dependency_event = threading.Event()

    dependency = build_handler(original_dependency_event)
    bot.default(
        build_handler(handler_event),
        dependencies=[Depends(dependency)],
        dependency_overrides_provider=None,
    )

    bot.dependency_overrides[dependency] = build_handler(fake_dependency_event)

    await client.send_command(incoming_message)

    assert handler_event.is_set()
    assert not original_dependency_event.is_set()
    assert fake_dependency_event.is_set()


async def test_overrider_is_used_if_not_none(
    bot,
    client,
    incoming_message,
    build_handler,
):
    handler_event = threading.Event()
    original_dependency_event = threading.Event()
    fake_dependency_event = threading.Event()

    dependency = build_handler(original_dependency_event)
    bot.default(
        build_handler(handler_event),
        dependencies=[Depends(dependency)],
        dependency_overrides_provider={},
    )

    bot.dependency_overrides[dependency] = build_handler(fake_dependency_event)

    await client.send_command(incoming_message)

    assert handler_event.is_set()
    assert not fake_dependency_event.is_set()
    assert original_dependency_event.is_set()
