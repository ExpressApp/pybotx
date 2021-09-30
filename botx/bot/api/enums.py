from botx.bot.models.commands.enums import ClientPlatforms, UserKinds
from botx.shared_models.api_base import StrEnum


class BotAPICommandTypes(StrEnum):
    USER = "user"
    SYSTEM = "system"


class BotAPIClientPlatforms(StrEnum):
    WEB = "web"
    ANDROID = "android"
    IOS = "ios"
    DESKTOP = "desktop"


class BotAPIUserKinds(StrEnum):
    USER = "user"
    CTS_USER = "cts_user"
    BOTX = "botx"


def convert_client_platform(client_platform: BotAPIClientPlatforms) -> ClientPlatforms:
    client_platforms_mapping = {
        BotAPIClientPlatforms.WEB: ClientPlatforms.WEB,
        BotAPIClientPlatforms.ANDROID: ClientPlatforms.ANDROID,
        BotAPIClientPlatforms.IOS: ClientPlatforms.IOS,
        BotAPIClientPlatforms.DESKTOP: ClientPlatforms.DESKTOP,
    }

    converted_type = client_platforms_mapping.get(client_platform)
    if converted_type is None:
        raise NotImplementedError(f"Unsupported client platform: {client_platform}")

    return converted_type


def convert_user_kind(user_kind: BotAPIUserKinds) -> UserKinds:
    user_kinds_mapping = {
        BotAPIUserKinds.USER: UserKinds.RTS_USER,
        BotAPIUserKinds.CTS_USER: UserKinds.CTS_USER,
        BotAPIUserKinds.BOTX: UserKinds.BOT,
    }

    converted_type = user_kinds_mapping.get(user_kind)
    if converted_type is None:
        raise NotImplementedError(f"Unsupported user kind: {user_kind}")

    return converted_type
