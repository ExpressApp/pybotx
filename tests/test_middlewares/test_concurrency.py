import pytest

from botx import Bot, IncomingMessage, Message, TestClient
from botx.middlewares.base import BaseMiddleware
from botx.typing import AsyncExecutor, Executor, SyncExecutor


class SyncMiddleware(BaseMiddleware):
    def __init__(self, executor: Executor) -> None:
        super().__init__(executor)
        self.flag = False

    def dispatch(self, message: Message, call_next: SyncExecutor) -> None:
        self.flag = True
        call_next(message)


class AsyncMiddleware(BaseMiddleware):
    def __init__(self, executor: Executor) -> None:
        super().__init__(executor)
        self.flag = False

    async def dispatch(self, message: Message, call_next: AsyncExecutor) -> None:
        self.flag = True
        await call_next(message)


@pytest.mark.asyncio
async def test_that_middleware_with_sync_dispatch_will_receive_blocking_executor(
    bot: Bot, client: TestClient, incoming_message: IncomingMessage
) -> None:
    bot.add_middleware(SyncMiddleware)
    bot.collector.default_message_handler = None

    flag = False

    @bot.default
    async def command_handler() -> None:
        nonlocal flag
        flag = True

    await client.send_command(incoming_message)
    assert flag

    executor = bot.exception_middleware.executor

    assert isinstance(executor, SyncMiddleware)
    assert executor.flag


@pytest.mark.asyncio
async def test_that_middleware_with_async_dispatch_will_receive_asynchronous_executor(
    bot: Bot, client: TestClient, incoming_message: IncomingMessage
) -> None:
    bot.add_middleware(AsyncMiddleware)
    bot.collector.default_message_handler = None

    flag = False

    @bot.default
    async def command_handler() -> None:
        nonlocal flag
        flag = True

    await client.send_command(incoming_message)
    assert flag

    executor = bot.exception_middleware.executor

    assert isinstance(executor, AsyncMiddleware)
    assert executor.flag


@pytest.mark.asyncio
async def test_that_both_async_and_sync_middlewares_will_work(
    bot: Bot, client: TestClient, incoming_message: IncomingMessage
) -> None:
    bot.add_middleware(SyncMiddleware)
    bot.add_middleware(AsyncMiddleware)
    bot.collector.default_message_handler = None

    flag = False

    @bot.default
    async def command_handler() -> None:
        nonlocal flag
        flag = True

    await client.send_command(incoming_message)
    assert flag

    executor = bot.exception_middleware.executor

    assert isinstance(executor, AsyncMiddleware)
    assert executor.flag

    executor = executor.executor
    assert isinstance(executor, SyncMiddleware)
    assert executor.flag
