from __future__ import annotations

from typing import Literal, TypeGuard
from uuid import UUID

from pybotx.presentation.contracts.api_base import VerifiedPayloadBaseModel
from pybotx.presentation.contracts.enums import APIAttachmentTypes
from pybotx.domain.models.attachments import (
    AttachmentDocument,
    AttachmentImage,
    AttachmentVideo,
    AttachmentVoice,
    Contact,
    IncomingAttachment,
    Link,
    Location,
    Sticker,
    decode_rfc2397,
    get_attachment_extension_from_encoded_content,
)
from pybotx.domain.models.enums import AttachmentTypes


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
    location_lat: str | float
    location_lng: str | float


class BotAPIAttachmentLocation(VerifiedPayloadBaseModel):
    type: Literal[APIAttachmentTypes.LOCATION]
    data: BotAPIAttachmentLocationData


class BotAPIAttachmentContactData(VerifiedPayloadBaseModel):
    contact_name: str


class BotAPIAttachmentContact(VerifiedPayloadBaseModel):
    type: Literal[APIAttachmentTypes.CONTACT]
    data: BotAPIAttachmentContactData


class BotAPIAttachmentStickerData(VerifiedPayloadBaseModel):
    id: UUID
    link: str
    pack: UUID


class BotAPIAttachmentSticker(VerifiedPayloadBaseModel):
    type: Literal[APIAttachmentTypes.STICKER]
    data: BotAPIAttachmentStickerData


class BotAPIAttachmentLinkData(VerifiedPayloadBaseModel):
    url: str
    url_title: str
    url_preview: str
    url_text: str


class BotAPIAttachmentLink(VerifiedPayloadBaseModel):
    type: Literal[APIAttachmentTypes.LINK]
    data: BotAPIAttachmentLinkData


BotAPIAttachment = (
    BotAPIAttachmentVideo
    | BotAPIAttachmentImage
    | BotAPIAttachmentDocument
    | BotAPIAttachmentVoice
    | BotAPIAttachmentLocation
    | BotAPIAttachmentContact
    | BotAPIAttachmentLink
    | BotAPIAttachmentSticker
)


def _is_api_image_attachment(
    attachment: BotAPIAttachment,
) -> TypeGuard[BotAPIAttachmentImage]:
    return attachment.type == APIAttachmentTypes.IMAGE


def _is_api_video_attachment(
    attachment: BotAPIAttachment,
) -> TypeGuard[BotAPIAttachmentVideo]:
    return attachment.type == APIAttachmentTypes.VIDEO


def _is_api_document_attachment(
    attachment: BotAPIAttachment,
) -> TypeGuard[BotAPIAttachmentDocument]:
    return attachment.type == APIAttachmentTypes.DOCUMENT


def _is_api_voice_attachment(
    attachment: BotAPIAttachment,
) -> TypeGuard[BotAPIAttachmentVoice]:
    return attachment.type == APIAttachmentTypes.VOICE


def _is_api_location_attachment(
    attachment: BotAPIAttachment,
) -> TypeGuard[BotAPIAttachmentLocation]:
    return attachment.type == APIAttachmentTypes.LOCATION


def _is_api_contact_attachment(
    attachment: BotAPIAttachment,
) -> TypeGuard[BotAPIAttachmentContact]:
    return attachment.type == APIAttachmentTypes.CONTACT


def _is_api_link_attachment(
    attachment: BotAPIAttachment,
) -> TypeGuard[BotAPIAttachmentLink]:
    return attachment.type == APIAttachmentTypes.LINK


def _is_api_sticker_attachment(
    attachment: BotAPIAttachment,
) -> TypeGuard[BotAPIAttachmentSticker]:
    return attachment.type == APIAttachmentTypes.STICKER


def convert_api_attachment_to_domain(
    api_attachment: BotAPIAttachment,
    message_body: str,
) -> IncomingAttachment:
    match api_attachment.type:
        case APIAttachmentTypes.IMAGE:
            if not _is_api_image_attachment(api_attachment):
                raise NotImplementedError(
                    f"Unsupported attachment type: {api_attachment.type}",
                )
            content = decode_rfc2397(api_attachment.data.content)

            return AttachmentImage(
                type=AttachmentTypes.IMAGE,
                filename=api_attachment.data.file_name,
                size=len(content),
                is_async_file=False,
                content=content,
            )
        case APIAttachmentTypes.VIDEO:
            if not _is_api_video_attachment(api_attachment):
                raise NotImplementedError(
                    f"Unsupported attachment type: {api_attachment.type}",
                )
            content = decode_rfc2397(api_attachment.data.content)

            return AttachmentVideo(
                type=AttachmentTypes.VIDEO,
                filename=api_attachment.data.file_name,
                size=len(content),
                is_async_file=False,
                content=content,
                duration=api_attachment.data.duration,
            )
        case APIAttachmentTypes.DOCUMENT:
            if not _is_api_document_attachment(api_attachment):
                raise NotImplementedError(
                    f"Unsupported attachment type: {api_attachment.type}",
                )
            content = decode_rfc2397(api_attachment.data.content)

            return AttachmentDocument(
                type=AttachmentTypes.DOCUMENT,
                filename=api_attachment.data.file_name,
                size=len(content),
                is_async_file=False,
                content=content,
            )
        case APIAttachmentTypes.VOICE:
            if not _is_api_voice_attachment(api_attachment):
                raise NotImplementedError(
                    f"Unsupported attachment type: {api_attachment.type}",
                )
            content = decode_rfc2397(api_attachment.data.content)
            attachment_extension = get_attachment_extension_from_encoded_content(
                api_attachment.data.content,
            )

            return AttachmentVoice(
                type=AttachmentTypes.VOICE,
                filename=f"record.{attachment_extension}",
                size=len(content),
                is_async_file=False,
                content=content,
                duration=api_attachment.data.duration,
            )
        case APIAttachmentTypes.LOCATION:
            if not _is_api_location_attachment(api_attachment):
                raise NotImplementedError(
                    f"Unsupported attachment type: {api_attachment.type}",
                )

            return Location(
                name=api_attachment.data.location_name,
                address=api_attachment.data.location_address,
                latitude=str(api_attachment.data.location_lat),
                longitude=str(api_attachment.data.location_lng),
            )
        case APIAttachmentTypes.CONTACT:
            if not _is_api_contact_attachment(api_attachment):
                raise NotImplementedError(
                    f"Unsupported attachment type: {api_attachment.type}",
                )

            return Contact(
                name=api_attachment.data.contact_name,
            )
        case APIAttachmentTypes.LINK:
            if not _is_api_link_attachment(api_attachment):
                raise NotImplementedError(
                    f"Unsupported attachment type: {api_attachment.type}",
                )

            return Link(
                url=api_attachment.data.url,
                title=api_attachment.data.url_title,
                preview=api_attachment.data.url_preview,
                text=api_attachment.data.url_text,
            )
        case APIAttachmentTypes.STICKER:
            if not _is_api_sticker_attachment(api_attachment):
                raise NotImplementedError(
                    f"Unsupported attachment type: {api_attachment.type}",
                )

            return Sticker(
                id=api_attachment.data.id,
                image_link=api_attachment.data.link,
                pack_id=api_attachment.data.pack,
                emoji=message_body,
            )
        case _:
            raise NotImplementedError(
                f"Unsupported attachment type: {api_attachment.type}",
            )
