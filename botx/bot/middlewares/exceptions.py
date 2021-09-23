from typing import TYPE_CHECKING, Awaitable, Callable, Dict, Optional, Type

from loguru import logger

from botx.bot.handler import IncomingMessageHandlerFunc
from botx.bot.models.commands.incoming_message import IncomingMessage

if TYPE_CHECKING:  # To avoid circular import
    from botx.bot.bot import Bot

ExceptionHandler = Callable[
    [Exception, IncomingMessage, "Bot"],
    Awaitable[None],
]


class ExceptionMiddleware:
    """Exception handling middleware."""

    def __init__(self) -> None:
        self._exception_handlers: Dict[Type[Exception], ExceptionHandler] = {}

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
                exc_name = type(message_handler_exc).__name__
                logger.exception(
                    f"Uncaught exception {exc_name}:",
                    message_handler_exc,
                )
                return

            try:  # noqa: WPS505
                await exception_handler(message_handler_exc, message, bot)
            except Exception as error_handler_exc:
                exc_name = type(message_handler_exc).__name__
                logger.exception(
                    f"Uncaught exception {exc_name} in exception handler:",
                    error_handler_exc,
                )

    def add_exception_handler(
        self,
        exc_class: Type[Exception],
        handler: ExceptionHandler,
    ) -> None:
        self._exception_handlers[exc_class] = handler

    def _get_exception_handler(self, exc: Exception) -> Optional[ExceptionHandler]:
        for exc_cls in type(exc).mro():
            handler = self._exception_handlers.get(exc_cls)
            if handler:
                return handler

        return None
