from dataclasses import dataclass
from typing import Any, Dict, Optional
from uuid import UUID


@dataclass
class BotCommandBase:
    bot_id: UUID
    raw_command: Optional[Dict[str, Any]]
