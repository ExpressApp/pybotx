from dataclasses import dataclass
from typing import Any, Dict, Literal, Union, cast
from uuid import UUID

from pybotx.models.api_base import VerifiedPayloadBaseModel
from pybotx.models.enums import (
    APIAttachmentTypes,
    AttachmentTypes,
    convert_attachment_type_from_domain,
    convert_attachment_type_to_domain,
)


@dataclass
class FileMeta:
    id: UUID
    url: str
    name: str
    size: int
    mimetype: str
    hash: str

    async def dumps(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "url": self.url,
            "name": self.name,
            "size": self.size,
            "mimetype": self.mimetype,
            "hash": self.hash,
        }


@dataclass
class AsyncFileBase:
    type: AttachmentTypes
    is_async_file: Literal[True]
    meta: FileMeta


@dataclass
class Image(AsyncFileBase):
    type: Literal[AttachmentTypes.IMAGE]


@dataclass
class Video(AsyncFileBase):
    type: Literal[AttachmentTypes.VIDEO]

    duration: int


@dataclass
class Document(AsyncFileBase):
    type: Literal[AttachmentTypes.DOCUMENT]


@dataclass
class Voice(AsyncFileBase):
    type: Literal[AttachmentTypes.VOICE]

    duration: int


class APIAsyncFileBase(VerifiedPayloadBaseModel):
    type: APIAttachmentTypes
    file: str
    file_mime_type: str
    file_id: UUID
    file_name: str
    file_size: int
    file_hash: str

    class Config:
        """BotX sends extra fields which are used by client only.

        We skip their validation, but extra fields will be saved during
        serialization/deserialization.
        """

        extra = "allow"


class ApiAsyncFileImage(APIAsyncFileBase):
    type: Literal[APIAttachmentTypes.IMAGE]


class ApiAsyncFileVideo(APIAsyncFileBase):
    type: Literal[APIAttachmentTypes.VIDEO]

    duration: int


class ApiAsyncFileDocument(APIAsyncFileBase):
    type: Literal[APIAttachmentTypes.DOCUMENT]


class ApiAsyncFileVoice(APIAsyncFileBase):
    type: Literal[APIAttachmentTypes.VOICE]

    duration: int


APIAsyncFile = Union[
    ApiAsyncFileImage,
    ApiAsyncFileVideo,
    ApiAsyncFileDocument,
    ApiAsyncFileVoice,
]

File = Union[Image, Video, Document, Voice]


def convert_async_file_from_domain(file: File) -> APIAsyncFile:
    attachment_type = convert_attachment_type_from_domain(file.type)

    if attachment_type == APIAttachmentTypes.IMAGE:
        attachment_type = cast(Literal[APIAttachmentTypes.IMAGE], attachment_type)
        file = cast(Image, file)

        return ApiAsyncFileImage(
            type=attachment_type,
            file_name=file.meta.name,
            file_size=file.meta.size,
            file_id=file.meta.id,
            file=file.meta.url,
            file_mime_type=file.meta.mimetype,
            file_hash=file.meta.hash,
        )

    if attachment_type == APIAttachmentTypes.VIDEO:
        attachment_type = cast(Literal[APIAttachmentTypes.VIDEO], attachment_type)
        file = cast(Video, file)

        return ApiAsyncFileVideo(
            type=attachment_type,
            file_name=file.meta.name,
            file_size=file.meta.size,
            duration=file.duration,
            file_id=file.meta.id,
            file=file.meta.url,
            file_mime_type=file.meta.mimetype,
            file_hash=file.meta.hash,
        )

    if attachment_type == APIAttachmentTypes.DOCUMENT:
        attachment_type = cast(Literal[APIAttachmentTypes.DOCUMENT], attachment_type)
        file = cast(Document, file)

        return ApiAsyncFileDocument(
            type=attachment_type,
            file_name=file.meta.name,
            file_size=file.meta.size,
            file_id=file.meta.id,
            file=file.meta.url,
            file_mime_type=file.meta.mimetype,
            file_hash=file.meta.hash,
        )

    if attachment_type == APIAttachmentTypes.VOICE:
        attachment_type = cast(Literal[APIAttachmentTypes.VOICE], attachment_type)
        file = cast(Voice, file)

        return ApiAsyncFileVoice(
            type=attachment_type,
            file_name=file.meta.name,
            file_size=file.meta.size,
            duration=file.duration,
            file_id=file.meta.id,
            file=file.meta.url,
            file_mime_type=file.meta.mimetype,
            file_hash=file.meta.hash,
        )

    raise NotImplementedError(f"Unsupported attachment type: {attachment_type}")


def convert_async_file_to_domain(async_file: APIAsyncFile) -> File:
    attachment_type = convert_attachment_type_to_domain(async_file.type)

    if attachment_type == AttachmentTypes.IMAGE:
        attachment_type = cast(Literal[AttachmentTypes.IMAGE], attachment_type)
        async_file = cast(ApiAsyncFileImage, async_file)
        async_file_meta = FileMeta(
            id=async_file.file_id,
            name=async_file.file_name,
            size=async_file.file_size,
            mimetype=async_file.file_mime_type,
            url=async_file.file,
            hash=async_file.file_hash,
        )

        return Image(
            type=attachment_type,
            is_async_file=True,
            meta=async_file_meta,
        )

    if attachment_type == AttachmentTypes.VIDEO:
        attachment_type = cast(Literal[AttachmentTypes.VIDEO], attachment_type)
        async_file = cast(ApiAsyncFileVideo, async_file)
        async_file_meta = FileMeta(
            id=async_file.file_id,
            name=async_file.file_name,
            size=async_file.file_size,
            mimetype=async_file.file_mime_type,
            url=async_file.file,
            hash=async_file.file_hash,
        )

        return Video(
            type=attachment_type,
            duration=async_file.duration,
            is_async_file=True,
            meta=async_file_meta,
        )

    if attachment_type == AttachmentTypes.DOCUMENT:
        attachment_type = cast(Literal[AttachmentTypes.DOCUMENT], attachment_type)
        async_file = cast(ApiAsyncFileDocument, async_file)
        async_file_meta = FileMeta(
            id=async_file.file_id,
            name=async_file.file_name,
            size=async_file.file_size,
            mimetype=async_file.file_mime_type,
            url=async_file.file,
            hash=async_file.file_hash,
        )

        return Document(
            type=attachment_type,
            is_async_file=True,
            meta=async_file_meta,
        )

    if attachment_type == AttachmentTypes.VOICE:
        attachment_type = cast(Literal[AttachmentTypes.VOICE], attachment_type)
        async_file = cast(ApiAsyncFileVoice, async_file)
        async_file_meta = FileMeta(
            id=async_file.file_id,
            name=async_file.file_name,
            size=async_file.file_size,
            mimetype=async_file.file_mime_type,
            url=async_file.file,
            hash=async_file.file_hash,
        )

        return Voice(
            type=attachment_type,
            duration=async_file.duration,
            is_async_file=True,
            meta=async_file_meta,
        )

    raise NotImplementedError(f"Unsupported attachment type: {attachment_type}")
