from enum import auto

from botx.bot.models.commands.enums import AutoName
from botx.shared_models.api_base import StrEnum


class ChatTypes(AutoName):
    PERSONAL_CHAT = auto()
    GROUP_CHAT = auto()
    CHANNEL = auto()


class APIChatTypes(StrEnum):
    CHAT = "chat"
    GROUP_CHAT = "group_chat"
    CHANNEL = "channel"


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
