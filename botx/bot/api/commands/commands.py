from typing import Union

from botx.bot.api.commands.incoming_message import BotAPIIncomingMessage
from botx.bot.api.commands.system_events.chat_created import BotAPIChatCreated

BotAPICommand = Union[BotAPIChatCreated, BotAPIIncomingMessage]
