from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Literal


@dataclass
class BotAPIBotDisabledErrorData:
    status_message: str


@dataclass
class BotAPIBotDisabledResponse:
    error_data: BotAPIBotDisabledErrorData
    errors: List[str] = field(default_factory=list)
    reason: Literal["bot_disabled"] = "bot_disabled"


def build_bot_disabled_response(status_message: str) -> Dict[str, Any]:
    response = BotAPIBotDisabledResponse(
        error_data=BotAPIBotDisabledErrorData(status_message=status_message),
    )

    return asdict(response)
