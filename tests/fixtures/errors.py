import threading

import pytest

from botx import Message


@pytest.fixture()
def build_exception_catcher(storage):
    def factory(event: threading.Event):
        def decorator(exc: Exception, msg: Message):
            event.set()
            storage.exception = exc
            storage.message = msg

        return decorator

    return factory
