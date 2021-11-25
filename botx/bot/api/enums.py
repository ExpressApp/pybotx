from botx.bot.models.commands.enums import ClientPlatforms, MentionTypes
from botx.shared_models.api_base import StrEnum


class BotAPICommandTypes(StrEnum):
    USER = "user"
    SYSTEM = "system"


class BotAPIClientPlatforms(StrEnum):
    WEB = "web"
    ANDROID = "android"
    IOS = "ios"
    DESKTOP = "desktop"


class BotAPIEntityTypes(StrEnum):
    MENTION = "mention"
    FORWARD = "forward"
    REPLY = "reply"


class BotAPIMentionTypes(StrEnum):
    CONTACT = "contact"
    CHAT = "chat"
    CHANNEL = "channel"
    USER = "user"
    ALL = "all"


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


def convert_mention_type_to_domain(mention_type: BotAPIMentionTypes) -> MentionTypes:
    mention_types_mapping = {
        BotAPIMentionTypes.CONTACT: MentionTypes.CONTACT,
        BotAPIMentionTypes.CHAT: MentionTypes.CHAT,
        BotAPIMentionTypes.CHANNEL: MentionTypes.CHANNEL,
        BotAPIMentionTypes.USER: MentionTypes.USER,
        BotAPIMentionTypes.ALL: MentionTypes.ALL,
    }

    converted_type = mention_types_mapping.get(mention_type)
    if converted_type is None:
        raise NotImplementedError(f"Unsupported mention type: {mention_type}")

    return converted_type


def convert_mention_type_from_domain(
    mention_type: MentionTypes,
) -> BotAPIMentionTypes:
    embed_mention_types_mapping = {
        MentionTypes.USER: BotAPIMentionTypes.USER,
        MentionTypes.CONTACT: BotAPIMentionTypes.CONTACT,
        MentionTypes.CHAT: BotAPIMentionTypes.CHAT,
        MentionTypes.CHANNEL: BotAPIMentionTypes.CHANNEL,
        MentionTypes.ALL: BotAPIMentionTypes.ALL,
    }

    converted_type = embed_mention_types_mapping.get(mention_type)
    if converted_type is None:
        raise NotImplementedError(f"Unsupported mention type: {mention_type}")

    return converted_type
