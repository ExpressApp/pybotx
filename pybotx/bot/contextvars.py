from contextvars import ContextVar
from typing import TYPE_CHECKING
from uuid import UUID

if TYPE_CHECKING:  # To avoid circular import
    from pybotx.bot.bot import Bot

bot_var: ContextVar["Bot"] = ContextVar("bot_var")
bot_id_var: ContextVar[UUID] = ContextVar("bot_id")
chat_id_var: ContextVar[UUID] = ContextVar("chat_id")
