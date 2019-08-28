import json
from typing import Any, Dict, Optional


class BotXException(Exception):
    def __init__(self, message: str = "", data: Optional[Dict[str, Any]] = None):
        self.message = message
        self.data = data

        msg = ""

        if message:
            msg = f"\n[msg] -> {message}"
        if data:
            msg += f"\n[data] -> {json.dumps(data, indent=4)}"

        super().__init__(msg)


class BotXAPIException(BotXException):
    pass


class BotXDependencyFailure(BotXException):
    pass


class BotXValidationError(BotXException):
    pass
