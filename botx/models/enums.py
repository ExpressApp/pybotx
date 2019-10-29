from enum import Enum


class StatusEnum(str, Enum):
    ok: str = "ok"
    error: str = "error"


class ResponseRecipientsEnum(str, Enum):
    all: str = "all"


class ChatTypeEnum(str, Enum):
    chat: str = "chat"
    group_chat: str = "group_chat"
    channel: str = "channel"


class MentionTypeEnum(str, Enum):
    user: str = "user"
    all: str = "all"
    cts: str = "cts"
    channel: str = "channel"


class SystemEventsEnum(str, Enum):
    chat_created: str = "system:chat_created"


class UserKindEnum(str, Enum):
    bot: str = "botx"
    user: str = "user"
    cts_user: str = "cts_user"


class CommandTypeEnum(str, Enum):
    user: str = "user"
    system: str = "system"
