import threading

import pytest

pytestmark = pytest.mark.asyncio
pytest_plugins = ("tests.test_middlewares.test_concurrency.fixtures",)


@pytest.mark.parametrize(
    "order",
    [("sync", "sync"), ("sync", "async"), ("async", "sync"), ("async", "async")],
)
async def test_that_both_async_and_sync_middlewares_will_work(
    bot,
    client,
    incoming_message,
    async_middleware_class,
    sync_middleware_class,
    build_handler,
    order,
):
    event = threading.Event()

    if order[0] == "sync":
        bot.add_middleware(sync_middleware_class)
    else:
        bot.add_middleware(async_middleware_class)

    if order[1] == "sync":
        bot.add_middleware(sync_middleware_class)
    else:
        bot.add_middleware(async_middleware_class)

    bot.default(build_handler(event))

    await client.send_command(incoming_message)

    assert event.is_set()

    middleware1 = bot.exception_middleware.executor
    assert middleware1.event.is_set()

    middleware2 = middleware1.executor
    assert middleware2.event.is_set()
