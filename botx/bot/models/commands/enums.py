from enum import Enum, auto


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


class ClientPlatforms(AutoName):
    WEB = auto()
    ANDROID = auto()
    IOS = auto()
    DESKTOP = auto()


class AttachmentTypes(AutoName):
    IMAGE = auto()
    VIDEO = auto()
    DOCUMENT = auto()
    VOICE = auto()
    LOCATION = auto()
    CONTACT = auto()
    LINK = auto()


class MentionTypes(AutoName):
    CONTACT = auto()
    CHAT = auto()
    CHANNEL = auto()
    USER = auto()
    ALL = auto()
