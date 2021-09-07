from typing import Union

from botx.api.bot_api.chat_created import BotAPIChatCreated
from botx.api.bot_api.incoming_message import BotAPIIncomingMessage

BotAPICommand = Union[BotAPIChatCreated, BotAPIIncomingMessage]
