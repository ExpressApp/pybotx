from botx.bot.models.commands.enums import AttachmentTypes
from botx.shared_models.api_base import StrEnum
from botx.shared_models.domain.enums import ChatTypes


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


class APIAttachmentTypes(StrEnum):
    IMAGE = "image"
    VIDEO = "video"
    DOCUMENT = "document"
    VOICE = "voice"
    LOCATION = "location"
    CONTACT = "contact"
    LINK = "link"


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
    }

    converted_type = attachment_types_mapping.get(attachment_type)
    if converted_type is None:
        raise NotImplementedError(f"Unsupported attachment type: {attachment_type}")

    return converted_type
