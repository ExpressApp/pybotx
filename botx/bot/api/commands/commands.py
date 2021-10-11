from typing import Union

from botx.bot.api.commands.incoming_message import BotAPIIncomingMessage
from botx.bot.api.commands.system_events.added_to_chat import BotAPIAddedToChat
from botx.bot.api.commands.system_events.chat_created import BotAPIChatCreated

BotAPISystemEvent = Union[BotAPIChatCreated, BotAPIAddedToChat]

BotAPICommand = Union[BotAPIIncomingMessage, BotAPISystemEvent]
