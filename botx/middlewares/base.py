"""Definition of base for custom middlewares."""

from typing import Optional

from botx import concurrency
from botx.models import messages
from botx.typing import Executor, MiddlewareDispatcher


class BaseMiddleware:
    """Base middleware entity."""

    def __init__(
        self, executor: Executor, dispatch: Optional[MiddlewareDispatcher] = None
    ) -> None:
        """Init middleware with required params.

        Arguments:
            executor: callable object that accept message and will be executed after
                middlewares.
            dispatch: middleware logic executor.
        """
        self.executor = executor
        self.dispatch_func = dispatch or self.dispatch

    async def __call__(self, message: messages.Message) -> None:
        """Call middleware dispatcher as normal handler executor.

        Arguments:
            message: incoming message.
        """
        await concurrency.callable_to_coroutine(
            self.dispatch_func, message, self.executor
        )

    async def dispatch(self, message: messages.Message, call_next: Executor) -> None:
        """Execute middleware logic.

        Arguments:
            message: incoming message.
            call_next: next executor in middleware chain.
        """
        raise NotImplementedError()
