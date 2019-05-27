from pydantic import BaseModel


class BotXException(Exception):
    pass


class BotXObject(BaseModel):
    pass


class BotXEndpoint(BotXObject):
    method: str
    url: str


class BotXAPI(BotXObject):
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
