from enum import Enum, auto

from pybotx.models.api_base import StrEnum


class AutoName(Enum):
    def _generate_next_value_(  # type: ignore  # noqa: WPS120
        name,  # noqa: N805 (copied from official python docs)
        start,
        count,
        last_values,
    ):
        return name


class UserKinds(AutoName):
    RTS_USER = auto()
    CTS_USER = auto()
    BOT = auto()


class AttachmentTypes(AutoName):
    IMAGE = auto()
    VIDEO = auto()
    DOCUMENT = auto()
    VOICE = auto()
    LOCATION = auto()
    CONTACT = auto()
    LINK = auto()
    STICKER = auto()


class ClientPlatforms(AutoName):
    WEB = auto()
    ANDROID = auto()
    IOS = auto()
    DESKTOP = auto()


class MentionTypes(AutoName):
    CONTACT = auto()
    CHAT = auto()
    CHANNEL = auto()
    USER = auto()
    ALL = auto()


class ChatTypes(AutoName):
    """BotX chat types.

    Attributes:
        PERSONAL_CHAT: Personal chat with user.
        GROUP_CHAT: Group chat.
        CHANNEL: Public channel.
    """

    PERSONAL_CHAT = auto()
    GROUP_CHAT = auto()
    CHANNEL = auto()


class APIChatTypes(StrEnum):
    CHAT = "chat"
    GROUP_CHAT = "group_chat"
    CHANNEL = "channel"


class BotAPICommandTypes(StrEnum):
    USER = "user"
    SYSTEM = "system"


class BotAPISystemEventTypes(StrEnum):
    ADDED_TO_CHAT = "system:added_to_chat"
    CHAT_CREATED = "system:chat_created"
    CTS_LOGIN = "system:cts_login"
    CTS_LOGOUT = "system:cts_logout"
    DELETED_FROM_CHAT = "system:deleted_from_chat"
    INTERNAL_BOT_NOTIFICATION = "system:internal_bot_notification"
    LEFT_FROM_CHAT = "system:left_from_chat"
    SMARTAPP_EVENT = "system:smartapp_event"


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


class APIUserKinds(StrEnum):
    USER = "user"
    CTS_USER = "cts_user"
    BOTX = "botx"


class APIAttachmentTypes(StrEnum):
    IMAGE = "image"
    VIDEO = "video"
    DOCUMENT = "document"
    VOICE = "voice"
    LOCATION = "location"
    CONTACT = "contact"
    LINK = "link"
    STICKER = "sticker"


def convert_client_platform_to_domain(
    client_platform: BotAPIClientPlatforms,
) -> ClientPlatforms:
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


def convert_user_kind_to_domain(user_kind: APIUserKinds) -> UserKinds:
    user_kinds_mapping = {
        APIUserKinds.USER: UserKinds.RTS_USER,
        APIUserKinds.CTS_USER: UserKinds.CTS_USER,
        APIUserKinds.BOTX: UserKinds.BOT,
    }

    converted_type = user_kinds_mapping.get(user_kind)
    if converted_type is None:
        raise NotImplementedError(f"Unsupported user kind: {user_kind}")

    return converted_type


def convert_attachment_type_to_domain(
    attachment_type: APIAttachmentTypes,
) -> AttachmentTypes:
    attachment_types_mapping = {
        APIAttachmentTypes.IMAGE: AttachmentTypes.IMAGE,
        APIAttachmentTypes.VIDEO: AttachmentTypes.VIDEO,
        APIAttachmentTypes.DOCUMENT: AttachmentTypes.DOCUMENT,
        APIAttachmentTypes.VOICE: AttachmentTypes.VOICE,
        APIAttachmentTypes.LOCATION: AttachmentTypes.LOCATION,
        APIAttachmentTypes.CONTACT: AttachmentTypes.CONTACT,
        APIAttachmentTypes.LINK: AttachmentTypes.LINK,
        APIAttachmentTypes.STICKER: AttachmentTypes.STICKER,
    }

    converted_type = attachment_types_mapping.get(attachment_type)
    if converted_type is None:
        raise NotImplementedError(f"Unsupported attachment type: {attachment_type}")

    return converted_type


def convert_attachment_type_from_domain(
    attachment_type: AttachmentTypes,
) -> APIAttachmentTypes:
    attachment_types_mapping = {
        AttachmentTypes.IMAGE: APIAttachmentTypes.IMAGE,
        AttachmentTypes.VIDEO: APIAttachmentTypes.VIDEO,
        AttachmentTypes.DOCUMENT: APIAttachmentTypes.DOCUMENT,
        AttachmentTypes.VOICE: APIAttachmentTypes.VOICE,
        AttachmentTypes.LOCATION: APIAttachmentTypes.LOCATION,
        AttachmentTypes.CONTACT: APIAttachmentTypes.CONTACT,
        AttachmentTypes.LINK: APIAttachmentTypes.LINK,
    }

    converted_type = attachment_types_mapping.get(attachment_type)
    if converted_type is None:
        raise NotImplementedError(f"Unsupported attachment type: {attachment_type}")

    return converted_type


def convert_chat_type_from_domain(chat_type: ChatTypes) -> APIChatTypes:
    chat_types_mapping = {
        ChatTypes.PERSONAL_CHAT: APIChatTypes.CHAT,
        ChatTypes.GROUP_CHAT: APIChatTypes.GROUP_CHAT,
        ChatTypes.CHANNEL: APIChatTypes.CHANNEL,
    }

    converted_type = chat_types_mapping.get(chat_type)
    if converted_type is None:
        raise NotImplementedError(f"Unsupported chat type: {chat_type}")

    return converted_type


def convert_chat_type_to_domain(chat_type: APIChatTypes) -> ChatTypes:
    chat_types_mapping = {
        APIChatTypes.CHAT: ChatTypes.PERSONAL_CHAT,
        APIChatTypes.GROUP_CHAT: ChatTypes.GROUP_CHAT,
        APIChatTypes.CHANNEL: ChatTypes.CHANNEL,
    }

    converted_type = chat_types_mapping.get(chat_type)
    if converted_type is None:
        raise NotImplementedError(f"Unsupported chat type: {chat_type}")

    return converted_type
