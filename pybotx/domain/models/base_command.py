from dataclasses import dataclass
from typing import Any

from pybotx.domain.models.bot_account import BotAccount


@dataclass(slots=True)
class BotCommandBase:
    bot: BotAccount
    raw_command: dict[str, Any] | None
