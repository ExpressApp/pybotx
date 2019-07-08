import json
import re
from dataclasses import dataclass
from typing import Any, Dict, Optional

SYSTEM_FILE_TRANSFER = re.compile("file_transfer")
FILE_HANDLER_NAME = "file_receiver"

DEFAULT_HANDLER_BODY = re.compile("DEFAULT_HANDLER")

TEXT_MAX_LENGTH = 4096


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


@dataclass
class BotXEndpoint:
    method: str
    url: str


class BotXAPI:
    class V1:
        file: BotXEndpoint = BotXEndpoint(
            method="POST", url="https://{host}/api/v1/botx/file/callback"
        )

    class V2:
        command: BotXEndpoint = BotXEndpoint(
            method="POST", url="https://{host}/api/v2/botx/command/callback"
        )
        notification: BotXEndpoint = BotXEndpoint(
            method="POST", url="https://{host}/api/v2/botx/notification/callback"
        )
        token: BotXEndpoint = BotXEndpoint(
            method="GET", url="https://{host}/api/v2/botx/bots/{bot_id}/token"
        )

    class V3:
        command: BotXEndpoint = BotXEndpoint(
            method="POST", url="https://{host}/api/v3/botx/command/callback"
        )
        notification: BotXEndpoint = BotXEndpoint(
            method="POST", url="https://{host}/api/v3/botx/notification/callback"
        )