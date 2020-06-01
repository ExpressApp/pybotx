"""Middleware for retrieving tokens from BotX API before processing message."""

from botx.middlewares.base import BaseMiddleware
from botx.models.credentials import ServerCredentials
from botx.models.messages.message import Message
from botx.typing import AsyncExecutor


class AuthorizationMiddleware(BaseMiddleware):
    """Middleware for retrieving tokens from BotX API before processing message."""

    async def dispatch(self, message: Message, call_next: AsyncExecutor) -> None:
        """Obtain token for bot for handling answers to message.

        Arguments:
            message: incoming message.
            call_next: next executor in chain.
        """
        bot = message.bot
        server = bot.get_cts_by_host(message.host)
        if server.server_credentials is None:
            token = await bot.get_token(
                message.host,
                message.bot_id,
                server.calculate_signature(message.bot_id),
            )
            server.server_credentials = ServerCredentials(
                bot_id=message.bot_id, token=token,
            )
        await call_next(message)
