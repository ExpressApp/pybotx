"""Middleware for retrieving tokens from BotX API before processing message."""

from botx.middlewares.base import BaseMiddleware
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
        bot_account = bot.get_account_by_bot_id(message.bot_id)
        if bot_account.token is None:
            token = await bot.get_token(
                message.host,
                message.bot_id,
                bot_account.signature,
            )
            bot_account.token = token
        await call_next(message)
