import threading
from typing import Callable

import pytest

from botx import DependencyFailure, Depends

pytestmark = pytest.mark.asyncio


def build_botx_fail_dependency(event: threading.Event) -> Callable[[], None]:
    def factory():
        event.set()
        raise DependencyFailure

    return factory


@pytest.fixture()
def build_fail_dependency():
    return build_botx_fail_dependency


async def test_flow_stop_if_error_raised(
    bot, client, incoming_message, build_handler, build_fail_dependency,
):
    handler_event = threading.Event()

    dependency_event1 = threading.Event()
    dependency_event2 = threading.Event()
    dependency_event3 = threading.Event()

    bot.default(
        handler=build_handler(handler_event),
        dependencies=[
            Depends(build_handler(dependency_event1)),
            Depends(build_botx_fail_dependency(dependency_event2)),
            Depends(build_handler(dependency_event3)),
        ],
    )

    await client.send_command(incoming_message)

    assert dependency_event1.is_set()
    assert dependency_event2.is_set()
    assert not dependency_event3.is_set()
    assert not handler_event.is_set()
