from typing import Union

from botx.bot.api.commands.incoming_message import BotAPIIncomingMessage
from botx.bot.api.commands.system_events.added_to_chat import BotAPIAddedToChat
from botx.bot.api.commands.system_events.chat_created import BotAPIChatCreated
from botx.bot.api.commands.system_events.deleted_from_chat import BotAPIDeletedFromChat

BotAPISystemEvent = Union[BotAPIChatCreated, BotAPIAddedToChat, BotAPIDeletedFromChat]

BotAPICommand = Union[BotAPIIncomingMessage, BotAPISystemEvent]
