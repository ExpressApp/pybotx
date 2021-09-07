from botx.api.pydantic import StrEnum
from botx.enums import ChatTypes


class APIChatTypes(StrEnum):
    CHAT = "chat"
    GROUP_CHAT = "group_chat"
    CHANNEL = "channel"


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
