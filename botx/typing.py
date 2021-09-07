from typing import Union

from botx.incoming_message import IncomingMessage
from botx.system_events.typing import SystemEvent

BotXCommand = Union[IncomingMessage, SystemEvent]
