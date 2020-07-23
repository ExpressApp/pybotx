import threading
from typing import Optional

import pytest

from botx import Message
from botx.middlewares.ns import register_next_step_handler


@pytest.fixture()
def build_handler_to_start_chain():
    def factory(next_handler_name: Optional[str], event: threading.Event):
        def decorator(message: Message):
            event.set()
            if next_handler_name is not None:
                register_next_step_handler(message, next_handler_name)

        return decorator

    return factory
