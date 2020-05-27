import threading
from typing import Callable

import pytest


def build_botx_handler(event: threading.Event) -> Callable[[], None]:
    def factory():
        event.set()

    return factory


@pytest.fixture()
def build_handler():
    return build_botx_handler


@pytest.fixture()
def build_failed_handler():
    def factory(exception: Exception, event: threading.Event):
        def decorator():
            event.set()
            raise exception

        return decorator

    return factory
