from dataclasses import dataclass

SYSTEM_FILE_TRANSFER = "file_transfer"
FILE_HANDLER_NAME = "file_receiver"

DEFAULT_HANDLER_BODY = "DEFAULT_HANDLER"

PRIMITIVE_TYPES = {bool, int, float, str}
TEXT_MAX_LENGTH = 4096


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
