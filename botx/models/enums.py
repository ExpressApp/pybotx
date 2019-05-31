from enum import Enum


class StatusEnum(str, Enum):
    ok: str = "ok"
    error: str = "error"


class ResponseRecipientsEnum(str, Enum):
    all: str = "all"


class ChatTypeEnum(str, Enum):
    chat: str = "chat"
    group_chat: str = "group_chat"


class MentionTypeEnum(str, Enum):
    user: str = "user"
    all: str = "all"
    cts: str = "cts"
    channel: str = "channel"
