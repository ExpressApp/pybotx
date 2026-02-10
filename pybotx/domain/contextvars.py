from contextvars import ContextVar
from uuid import UUID

from pybotx.domain.ports.bot_access import BotAccessPort

bot_var: ContextVar[BotAccessPort] = ContextVar("bot_var")
bot_id_var: ContextVar[UUID] = ContextVar("bot_id")
chat_id_var: ContextVar[UUID] = ContextVar("chat_id")
