from enum import Enum, auto
from typing import Literal


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
        THREAD: Thread in a chat.
    """

    PERSONAL_CHAT = auto()
    GROUP_CHAT = auto()
    CHANNEL = auto()
    THREAD = auto()


class SyncSourceTypes(AutoName):
    AD = auto()
    ADMIN = auto()
    EMAIL = auto()
    OPENID = auto()
    BOTX = auto()


class ConferenceLinkTypes(AutoName):
    PUBLIC = auto()
    TRUSTS = auto()
    CORPORATE = auto()
    SERVER = auto()


UNSUPPORTED = Literal["UNSUPPORTED"]
IncomingChatTypes = ChatTypes | UNSUPPORTED
IncomingSyncSourceTypes = SyncSourceTypes | UNSUPPORTED


class StrEnum(str, Enum):  # (pydantic needs this inheritance)
    """Enum base for API models."""


class ChatLinkTypes(StrEnum):
    PUBLIC = "public"
    TRUSTS = "trusts"
    CORPORATE = "corporate"
    SERVER = "server"


class SmartappManifestWebLayoutChoices(StrEnum):
    minimal = "minimal"
    half = "half"
    full = "full"
