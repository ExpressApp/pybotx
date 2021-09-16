from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class BotCommandBase:
    raw_command: Optional[Dict[str, Any]]
