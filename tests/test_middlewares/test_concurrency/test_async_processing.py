import threading

import pytest

pytestmark = pytest.mark.asyncio
pytest_plugins = ("tests.test_middlewares.test_concurrency.fixtures",)


async def test_async_middleware_receives_async_executor(
    bot,
    client,
    incoming_message,
    build_handler,
    async_middleware_class,
):
    bot.add_middleware(async_middleware_class)

    event = threading.Event()
    bot.default(build_handler(event))

    await client.send_command(incoming_message)

    assert event.is_set()

    executor = bot.exception_middleware.executor

    assert isinstance(executor, async_middleware_class)
    assert executor.event.is_set()
