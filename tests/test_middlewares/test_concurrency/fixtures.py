import threading

import pytest

from botx import Message
from botx.middlewares.base import BaseMiddleware
from botx.typing import AsyncExecutor, Executor, SyncExecutor


class SyncMiddleware(BaseMiddleware):
    def __init__(self, executor: Executor) -> None:
        super().__init__(executor)
        self.event = threading.Event()

    def dispatch(self, message: Message, call_next: SyncExecutor) -> None:
        self.event.set()
        call_next(message)


class AsyncMiddleware(BaseMiddleware):
    def __init__(self, executor: Executor) -> None:
        super().__init__(executor)
        self.event = threading.Event()

    async def dispatch(self, message: Message, call_next: AsyncExecutor) -> None:
        self.event.set()
        await call_next(message)


@pytest.fixture()
def sync_middleware_class():
    return SyncMiddleware


@pytest.fixture()
def async_middleware_class():
    return AsyncMiddleware
