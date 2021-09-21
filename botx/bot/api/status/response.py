from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional

from botx.bot.models.status.bot_menu import BotMenu

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal  # type: ignore  # noqa: WPS440


@dataclass
class BotAPIBotMenuItem:
    description: str
    body: str
    name: str


BotAPIBotMenu = List[BotAPIBotMenuItem]


@dataclass
class BotAPIStatusResult:
    commands: BotAPIBotMenu
    enabled: Literal[True] = True
    status_message: Optional[str] = None


@dataclass
class BotAPIStatus:
    result: BotAPIStatusResult
    status: Literal["ok"] = "ok"


def build_bot_status_response(bot_menu: BotMenu) -> Dict[str, Any]:
    commands = [
        BotAPIBotMenuItem(body=command, name=command, description=description)
        for command, description in bot_menu.items()
    ]

    status = BotAPIStatus(
        result=BotAPIStatusResult(status_message="Bot is working", commands=commands),
    )
    return asdict(status)
