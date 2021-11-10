from botx.bot.models.commands.enums import AttachmentTypes, UserKinds
from botx.shared_models.api_base import StrEnum


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


def convert_user_kind(user_kind: APIUserKinds) -> UserKinds:
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
    }

    converted_type = attachment_types_mapping.get(attachment_type)
    if converted_type is None:
        raise NotImplementedError(f"Unsupported attachment type: {attachment_type}")

    return converted_type
