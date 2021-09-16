from typing import Union

from botx.bot.models.commands.incoming_message import IncomingMessage
from botx.bot.models.commands.system_events.chat_created import ChatCreatedEvent

SystemEvent = Union[ChatCreatedEvent]

BotCommand = Union[IncomingMessage, SystemEvent]
