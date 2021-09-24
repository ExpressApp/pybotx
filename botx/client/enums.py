from botx.api_base_models import StrEnum
from botx.bot.models.commands.enums import ChatTypes


class BotXAPIChatTypes(StrEnum):
    CHAT = "chat"
    GROUP_CHAT = "group_chat"
    CHANNEL = "channel"


def convert_chat_type_from_domain(chat_type: ChatTypes) -> BotXAPIChatTypes:
    chat_types_mapping = {
        ChatTypes.PERSONAL_CHAT: BotXAPIChatTypes.CHAT,
        ChatTypes.GROUP_CHAT: BotXAPIChatTypes.GROUP_CHAT,
        ChatTypes.CHANNEL: BotXAPIChatTypes.CHANNEL,
    }

    converted_type = chat_types_mapping.get(chat_type)
    if converted_type is None:
        raise NotImplementedError(f"Unsupported chat type: {chat_type}")

    return converted_type
