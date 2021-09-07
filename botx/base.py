from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class BotXCommandBase:
    raw_command: Optional[Dict[str, Any]]
