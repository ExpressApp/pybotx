import threading
from typing import Callable

import pytest

from botx import Bot

pytestmark = pytest.mark.asyncio


def build_lifespan_event(event: threading.Event) -> Callable[[Bot], None]:
    def factory(_bot):
        event.set()

    return factory


@pytest.fixture()
def build_lifespan():
    return build_lifespan_event


async def test_lifespan_events(bot, build_lifespan):
    startup_event = threading.Event()
    shutdown_event = threading.Event()

    bot.startup_events = [build_lifespan(startup_event)]
    bot.shutdown_events = [build_lifespan(shutdown_event)]

    await bot.start()
    assert startup_event.is_set()

    await bot.shutdown()
    assert shutdown_event.is_set()


async def test_no_error_when_stopping_bot_with_no_tasks(bot):
    await bot.shutdown()
