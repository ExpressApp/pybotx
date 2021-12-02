from typing import Union

from botx.bot.models.commands.incoming_message import IncomingMessage
from botx.models.system_events.added_to_chat import AddedToChatEvent
from botx.models.system_events.chat_created import ChatCreatedEvent
from botx.models.system_events.deleted_from_chat import DeletedFromChatEvent

SystemEvent = Union[ChatCreatedEvent, AddedToChatEvent, DeletedFromChatEvent]

BotCommand = Union[IncomingMessage, SystemEvent]
