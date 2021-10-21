import base64
from typing import Union, cast

from botx.bot.models.commands.enums import AttachmentTypes
from botx.shared_models.api.enums import (
    APIAttachmentTypes,
    convert_attachment_type_to_domain,
)
from botx.shared_models.api_base import VerifiedPayloadBaseModel
from botx.shared_models.domain.attachments import (
    AttachmentContact,
    AttachmentDocument,
    AttachmentImage,
    AttachmentLink,
    AttachmentLocation,
    AttachmentVideo,
    AttachmentVoice,
    IncomingAttachment,
)

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal  # type: ignore  # noqa: WPS440


class BotAPIAttachmentImageData(VerifiedPayloadBaseModel):
    content: str
    file_name: str


class BotAPIAttachmentImage(VerifiedPayloadBaseModel):
    type: Literal[APIAttachmentTypes.IMAGE]
    data: BotAPIAttachmentImageData


class BotAPIAttachmentVideoData(VerifiedPayloadBaseModel):
    content: str
    file_name: str
    duration: int


class BotAPIAttachmentVideo(VerifiedPayloadBaseModel):
    type: Literal[APIAttachmentTypes.VIDEO]
    data: BotAPIAttachmentVideoData


class BotAPIAttachmentDocumentData(VerifiedPayloadBaseModel):
    content: str
    file_name: str


class BotAPIAttachmentDocument(VerifiedPayloadBaseModel):
    type: Literal[APIAttachmentTypes.DOCUMENT]
    data: BotAPIAttachmentDocumentData


class BotAPIAttachmentVoiceData(VerifiedPayloadBaseModel):
    content: str
    duration: int


class BotAPIAttachmentVoice(VerifiedPayloadBaseModel):
    type: Literal[APIAttachmentTypes.VOICE]
    data: BotAPIAttachmentVoiceData


class BotAPIAttachmentLocationData(VerifiedPayloadBaseModel):
    location_name: str
    location_address: str
    location_lat: str
    location_lng: str


class BotAPIAttachmentLocation(VerifiedPayloadBaseModel):
    type: Literal[APIAttachmentTypes.LOCATION]
    data: BotAPIAttachmentLocationData


class BotAPIAttachmentContactData(VerifiedPayloadBaseModel):
    contact_name: str


class BotAPIAttachmentContact(VerifiedPayloadBaseModel):
    type: Literal[APIAttachmentTypes.CONTACT]
    data: BotAPIAttachmentContactData


class BotAPIAttachmentLinkData(VerifiedPayloadBaseModel):
    url: str
    url_title: str
    url_preview: str
    url_text: str


class BotAPIAttachmentLink(VerifiedPayloadBaseModel):
    type: Literal[APIAttachmentTypes.LINK]
    data: BotAPIAttachmentLinkData


BotAPIAttachment = Union[
    BotAPIAttachmentVideo,
    BotAPIAttachmentImage,
    BotAPIAttachmentDocument,
    BotAPIAttachmentVoice,
    BotAPIAttachmentLocation,
    BotAPIAttachmentContact,
    BotAPIAttachmentLink,
]


def convert_api_attachment_to_domain(
    api_attachment: BotAPIAttachment,
) -> IncomingAttachment:
    attachment_type = convert_attachment_type_to_domain(api_attachment.type)

    if attachment_type == AttachmentTypes.IMAGE:
        attachment_type = cast(Literal[AttachmentTypes.IMAGE], attachment_type)
        api_attachment = cast(BotAPIAttachmentImage, api_attachment)
        content = decode_rfc2397(api_attachment.data.content)

        return AttachmentImage(
            type=attachment_type,
            filename=api_attachment.data.file_name,
            size=len(content),
            content=content,
        )

    if attachment_type == AttachmentTypes.VIDEO:
        attachment_type = cast(Literal[AttachmentTypes.VIDEO], attachment_type)
        api_attachment = cast(BotAPIAttachmentVideo, api_attachment)
        content = decode_rfc2397(api_attachment.data.content)

        return AttachmentVideo(
            type=attachment_type,
            filename=api_attachment.data.file_name,
            size=len(content),
            content=content,
            duration=api_attachment.data.duration,
        )

    if attachment_type == AttachmentTypes.DOCUMENT:
        attachment_type = cast(Literal[AttachmentTypes.DOCUMENT], attachment_type)
        api_attachment = cast(BotAPIAttachmentDocument, api_attachment)
        content = decode_rfc2397(api_attachment.data.content)

        return AttachmentDocument(
            type=attachment_type,
            filename=api_attachment.data.file_name,
            size=len(content),
            content=content,
        )

    if attachment_type == AttachmentTypes.VOICE:
        attachment_type = cast(Literal[AttachmentTypes.VOICE], attachment_type)
        api_attachment = cast(BotAPIAttachmentVoice, api_attachment)
        content = decode_rfc2397(api_attachment.data.content)

        return AttachmentVoice(
            type=attachment_type,
            filename="record.mp3",
            size=len(content),
            content=content,
            duration=api_attachment.data.duration,
        )

    if attachment_type == AttachmentTypes.LOCATION:
        attachment_type = cast(Literal[AttachmentTypes.LOCATION], attachment_type)
        api_attachment = cast(BotAPIAttachmentLocation, api_attachment)

        return AttachmentLocation(
            type=attachment_type,
            name=api_attachment.data.location_name,
            address=api_attachment.data.location_address,
            latitude=api_attachment.data.location_lat,
            longitude=api_attachment.data.location_lng,
        )

    if attachment_type == AttachmentTypes.CONTACT:
        attachment_type = cast(Literal[AttachmentTypes.CONTACT], attachment_type)
        api_attachment = cast(BotAPIAttachmentContact, api_attachment)

        return AttachmentContact(
            type=attachment_type,
            name=api_attachment.data.contact_name,
        )

    if attachment_type == AttachmentTypes.LINK:
        attachment_type = cast(Literal[AttachmentTypes.LINK], attachment_type)
        api_attachment = cast(BotAPIAttachmentLink, api_attachment)

        return AttachmentLink(
            type=attachment_type,
            url=api_attachment.data.url,
            title=api_attachment.data.url_title,
            preview=api_attachment.data.url_preview,
            text=api_attachment.data.url_text,
        )

    raise NotImplementedError(f"Unsupported attachment type: {attachment_type}")


def decode_rfc2397(encoded_content: str) -> bytes:
    return base64.b64decode(encoded_content.split(",", 1)[1].encode())
