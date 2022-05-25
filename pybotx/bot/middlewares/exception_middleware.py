from typing import TYPE_CHECKING, Awaitable, Callable, Dict, Optional, Type

from pybotx.bot.handler import IncomingMessageHandlerFunc
from pybotx.logger import logger
from pybotx.models.message.incoming_message import IncomingMessage

if TYPE_CHECKING:  # To avoid circular import
    from pybotx.bot.bot import Bot

ExceptionHandler = Callable[
    [IncomingMessage, "Bot", Exception],
    Awaitable[None],
]
ExceptionHandlersDict = Dict[Type[Exception], ExceptionHandler]


class ExceptionMiddleware:
    """Exception handling middleware."""

    def __init__(self, exception_handlers: ExceptionHandlersDict) -> None:
        self._exception_handlers = exception_handlers

    async def dispatch(
        self,
        message: IncomingMessage,
        bot: "Bot",
        call_next: IncomingMessageHandlerFunc,
    ) -> None:
        try:
            await call_next(message, bot)
        except Exception as message_handler_exc:
            exception_handler = self._get_exception_handler(message_handler_exc)
            if exception_handler is None:
                raise message_handler_exc

            try:  # noqa: WPS505
                await exception_handler(message, bot, message_handler_exc)
            except Exception as error_handler_exc:
                exc_name = type(message_handler_exc).__name__
                logger.exception(
                    f"Uncaught exception {exc_name} in exception handler:",
                    error_handler_exc,
                )

    def _get_exception_handler(self, exc: Exception) -> Optional[ExceptionHandler]:
        for exc_cls in type(exc).mro():
            handler = self._exception_handlers.get(exc_cls)
            if handler:
                return handler

        return None
