from enum import Enum, auto
from typing import Literal, Optional, Union, overload


class AutoName(Enum):
    def _generate_next_value_(  # type: ignore
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
    UNREGISTERED = auto()
    GUEST = auto()


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
    AURORA = auto()


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


class SyncSourceTypes(AutoName):
    AD = auto()
    ADMIN = auto()
    EMAIL = auto()
    OPENID = auto()
    BOTX = auto()


UNSUPPORTED = Literal["UNSUPPORTED"]
IncomingChatTypes = Union[ChatTypes, UNSUPPORTED]
IncomingSyncSourceTypes = Union[SyncSourceTypes, UNSUPPORTED]


class StrEnum(str, Enum):  # noqa: WPS600 (pydantic needs this inheritance)
    """Enum base for API models."""

    # https://github.com/pydantic/pydantic/issues/3850
    # TODO: Use plain enums after migrating to Pydantic 2.0


class APIChatTypes(Enum):
    CHAT = "chat"
    GROUP_CHAT = "group_chat"
    CHANNEL = "channel"


class BotAPICommandTypes(StrEnum):
    USER = "user"
    SYSTEM = "system"


class BotAPISystemEventTypes(StrEnum):
    ADDED_TO_CHAT = "system:added_to_chat"
    CHAT_CREATED = "system:chat_created"
    CHAT_DELETED_BY_USER = "system:chat_deleted_by_user"
    CTS_LOGIN = "system:cts_login"
    CTS_LOGOUT = "system:cts_logout"
    DELETED_FROM_CHAT = "system:deleted_from_chat"
    INTERNAL_BOT_NOTIFICATION = "system:internal_bot_notification"
    LEFT_FROM_CHAT = "system:left_from_chat"
    SMARTAPP_EVENT = "system:smartapp_event"
    EVENT_EDIT = "system:event_edit"


class BotAPIClientPlatforms(Enum):
    WEB = "web"
    ANDROID = "android"
    IOS = "ios"
    DESKTOP = "desktop"
    AURORA = "aurora"


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


class APIUserKinds(Enum):
    USER = "user"
    CTS_USER = "cts_user"
    BOTX = "botx"
    UNREGISTERED = "unregistered"
    GUEST = "guest"


class APIAttachmentTypes(StrEnum):
    IMAGE = "image"
    VIDEO = "video"
    DOCUMENT = "document"
    VOICE = "voice"
    LOCATION = "location"
    CONTACT = "contact"
    LINK = "link"
    STICKER = "sticker"


class APISyncSourceTypes(Enum):
    AD = "ad"
    ADMIN = "admin"
    EMAIL = "email"
    OPENID = "openid"
    BOTX = "botx"


class SmartappManifestWebLayoutChoices(StrEnum):
    minimal = "minimal"
    half = "half"
    full = "full"


def convert_client_platform_to_domain(
    client_platform: BotAPIClientPlatforms,
) -> ClientPlatforms:
    client_platforms_mapping = {
        BotAPIClientPlatforms.WEB: ClientPlatforms.WEB,
        BotAPIClientPlatforms.ANDROID: ClientPlatforms.ANDROID,
        BotAPIClientPlatforms.IOS: ClientPlatforms.IOS,
        BotAPIClientPlatforms.DESKTOP: ClientPlatforms.DESKTOP,
        BotAPIClientPlatforms.AURORA: ClientPlatforms.AURORA,
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
        APIUserKinds.UNREGISTERED: UserKinds.UNREGISTERED,
        APIUserKinds.GUEST: UserKinds.GUEST,
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


@overload
def convert_chat_type_to_domain(
    chat_type: APIChatTypes,
) -> ChatTypes:
    ...  # noqa: WPS428


@overload
def convert_chat_type_to_domain(chat_type: str) -> UNSUPPORTED:
    ...  # noqa: WPS428


def convert_chat_type_to_domain(
    chat_type: Union[APIChatTypes, str],
) -> IncomingChatTypes:
    chat_types_mapping = {
        APIChatTypes.CHAT: ChatTypes.PERSONAL_CHAT,
        APIChatTypes.GROUP_CHAT: ChatTypes.GROUP_CHAT,
        APIChatTypes.CHANNEL: ChatTypes.CHANNEL,
    }

    converted_type: Optional[IncomingChatTypes]
    try:
        converted_type = chat_types_mapping.get(APIChatTypes(chat_type))
    except ValueError:
        converted_type = "UNSUPPORTED"

    if converted_type is None:
        raise NotImplementedError(f"Unsupported chat type: {chat_type}") from None

    return converted_type


@overload
def convert_sync_source_type_to_domain(
    sync_type: APISyncSourceTypes,
) -> SyncSourceTypes:
    ...  # noqa: WPS428


@overload
def convert_sync_source_type_to_domain(
    sync_type: str,
) -> UNSUPPORTED:
    ...  # noqa: WPS428


def convert_sync_source_type_to_domain(
    sync_type: Union[APISyncSourceTypes, str],
) -> IncomingSyncSourceTypes:
    sync_source_types_mapping = {
        APISyncSourceTypes.AD: SyncSourceTypes.AD,
        APISyncSourceTypes.ADMIN: SyncSourceTypes.ADMIN,
        APISyncSourceTypes.EMAIL: SyncSourceTypes.EMAIL,
        APISyncSourceTypes.OPENID: SyncSourceTypes.OPENID,
        APISyncSourceTypes.BOTX: SyncSourceTypes.BOTX,
    }

    converted_type: Optional[IncomingSyncSourceTypes]
    try:
        converted_type = sync_source_types_mapping.get(APISyncSourceTypes(sync_type))
    except ValueError:
        converted_type = "UNSUPPORTED"

    if converted_type is None:
        raise NotImplementedError(
            f"Unsupported sync source type: {sync_type}",
        ) from None

    return converted_type
