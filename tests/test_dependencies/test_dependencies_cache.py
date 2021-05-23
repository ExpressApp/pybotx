import threading
from typing import Callable

import pytest

from botx import Depends

pytestmark = pytest.mark.asyncio


def build_botx_dependency(lock: threading.Lock) -> Callable[[], None]:
    def factory():
        lock.acquire()

    return factory


@pytest.fixture()
def build_dependency():
    return build_botx_dependency


async def test_dependency_executed_only_once_per_message(
    bot,
    client,
    incoming_message,
    build_dependency,
    build_handler,
):
    event = threading.Event()
    lock = threading.Lock()

    dependency_function = build_dependency(lock)

    bot.default(
        build_handler(event),
        dependencies=[Depends(dependency_function), Depends(dependency_function)],
    )

    await client.send_command(incoming_message)

    assert event.is_set()
