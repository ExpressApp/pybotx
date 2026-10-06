from contextvars import ContextVar
from typing import TYPE_CHECKING
from uuid import UUID

from pybotx.models.bot_account import BotAccountKey

if TYPE_CHECKING:  # To avoid circular import
    from pybotx.bot.bot import Bot

bot_var: ContextVar["Bot"] = ContextVar("bot_var")
bot_id_var: ContextVar[UUID] = ContextVar("bot_id")
bot_account_key_var: ContextVar[BotAccountKey] = ContextVar("bot_account_key")
chat_id_var: ContextVar[UUID] = ContextVar("chat_id")
request_id_var: ContextVar[str] = ContextVar("request_id")
trace_id_var: ContextVar[str] = ContextVar("trace_id")
