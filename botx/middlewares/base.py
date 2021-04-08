"""Definition of base for custom middlewares.

Important:
    Middleware should implement `dispatch` method that can be a common function or
    an asynchronous function.

```python
class MyAsyncBotXMiddleware(BaseMiddleware):
    async def dispatch(
        self, message: Message, call_next: AsyncExecutor,
    ) -> None:
        await call_next(message)

class MySyncBotXMiddleware(BaseMiddleware):
    def dispatch(self, message: Message, call_next: SyncExecutor) -> None:
        call_next(message)
```
"""

from typing import Callable, Optional

from botx import concurrency
from botx.models.messages.message import Message
from botx.typing import Executor, MiddlewareDispatcher, SyncExecutor


def _default_dispatch(
    _middleware: "BaseMiddleware",
    _message: Message,
    _call_next: SyncExecutor,
) -> None:
    raise NotImplementedError


class BaseMiddleware:
    """Base middleware entity."""

    dispatch: Callable = _default_dispatch

    def __init__(
        self,
        executor: Executor,
        dispatch: Optional[MiddlewareDispatcher] = None,
    ) -> None:
        """Init middleware with required query_params.

        Arguments:
            executor: callable object that accept message and will be executed after
                middlewares.
            dispatch: middleware logic executor.
        """
        self.executor = executor
        self.dispatch_func = dispatch or self.dispatch

    async def __call__(self, message: Message) -> None:
        """Call middleware dispatcher as normal handler executor.

        Arguments:
            message: incoming message.
        """
        executor = self.executor
        if not concurrency.is_awaitable(self.dispatch_func):
            executor = concurrency.async_to_sync(self.executor)

        await concurrency.callable_to_coroutine(self.dispatch_func, message, executor)
