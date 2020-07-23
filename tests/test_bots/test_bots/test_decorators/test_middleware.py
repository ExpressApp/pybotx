import pytest

from botx import Message
from botx.typing import SyncExecutor


@pytest.fixture()
def middleware_function():
    def factory(_message: Message, _call_next: SyncExecutor):
        """Do nothing."""

    return factory


def test_register_middleware_through_decorator(bot, middleware_function):
    bot.middleware(middleware_function)
    assert bot.exception_middleware.executor.dispatch_func == middleware_function
