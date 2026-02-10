from __future__ import annotations

from typing import Literal, cast
from uuid import UUID

from pydantic import ConfigDict

from pybotx.infrastructure.contracts.api_base import VerifiedPayloadBaseModel
from pybotx.infrastructure.contracts.enums import (
    APIAttachmentTypes,
    convert_attachment_type_from_domain,
    convert_attachment_type_to_domain,
)
from pybotx.domain.missing import MissingOptional, Undefined
from pybotx.domain.models.async_files import Document, File, Image, Video, Voice
from pybotx.domain.models.enums import AttachmentTypes


class APIAsyncFileBase(VerifiedPayloadBaseModel):
    type: APIAttachmentTypes
    file: str
    file_mime_type: str
    file_id: UUID
    file_name: str
    file_size: int
    file_hash: str
    file_preview: MissingOptional[str] = Undefined
    file_preview_height: MissingOptional[int] = Undefined
    file_preview_width: MissingOptional[int] = Undefined
    file_encryption_algo: MissingOptional[str] = Undefined
    chunk_size: MissingOptional[int] = Undefined
    caption: MissingOptional[str] = Undefined

    model_config = ConfigDict(extra="allow", arbitrary_types_allowed=True)


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


APIAsyncFile = (
    ApiAsyncFileImage
    | ApiAsyncFileVideo
    | ApiAsyncFileDocument
    | ApiAsyncFileVoice
)


def _to_optional(value: MissingOptional[str | int]) -> str | int | None:
    if value is Undefined:
        return None
    return cast(str | int | None, value)


def _to_missing(value: str | int | None) -> MissingOptional[str | int]:
    return Undefined if value is None else value


def convert_async_file_from_domain(file: File) -> APIAsyncFile:
    attachment_type = convert_attachment_type_from_domain(file.type)

    if attachment_type == APIAttachmentTypes.IMAGE:
        file = cast(Image, file)

        return ApiAsyncFileImage(
            type=attachment_type,
            file_name=file.filename,
            file_size=file.size,
            file_id=file._file_id,
            file=file._file_url,
            file_mime_type=file._file_mimetype,
            file_hash=file._file_hash,
            file_preview=_to_missing(file.file_preview),
            file_preview_height=_to_missing(file.file_preview_height),
            file_preview_width=_to_missing(file.file_preview_width),
            file_encryption_algo=_to_missing(file.file_encryption_algo),
            chunk_size=_to_missing(file.chunk_size),
            caption=_to_missing(file.caption),
        )

    if attachment_type == APIAttachmentTypes.VIDEO:
        file = cast(Video, file)

        return ApiAsyncFileVideo(
            type=attachment_type,
            file_name=file.filename,
            file_size=file.size,
            duration=file.duration,
            file_id=file._file_id,
            file=file._file_url,
            file_mime_type=file._file_mimetype,
            file_hash=file._file_hash,
            file_preview=_to_missing(file.file_preview),
            file_preview_height=_to_missing(file.file_preview_height),
            file_preview_width=_to_missing(file.file_preview_width),
            file_encryption_algo=_to_missing(file.file_encryption_algo),
            chunk_size=_to_missing(file.chunk_size),
            caption=_to_missing(file.caption),
        )

    if attachment_type == APIAttachmentTypes.DOCUMENT:
        file = cast(Document, file)

        return ApiAsyncFileDocument(
            type=attachment_type,
            file_name=file.filename,
            file_size=file.size,
            file_id=file._file_id,
            file=file._file_url,
            file_mime_type=file._file_mimetype,
            file_hash=file._file_hash,
            file_preview=_to_missing(file.file_preview),
            file_preview_height=_to_missing(file.file_preview_height),
            file_preview_width=_to_missing(file.file_preview_width),
            file_encryption_algo=_to_missing(file.file_encryption_algo),
            chunk_size=_to_missing(file.chunk_size),
            caption=_to_missing(file.caption),
        )

    if attachment_type == APIAttachmentTypes.VOICE:
        file = cast(Voice, file)

        return ApiAsyncFileVoice(
            type=attachment_type,
            file_name=file.filename,
            file_size=file.size,
            duration=file.duration,
            file_id=file._file_id,
            file=file._file_url,
            file_mime_type=file._file_mimetype,
            file_hash=file._file_hash,
            file_preview=_to_missing(file.file_preview),
            file_preview_height=_to_missing(file.file_preview_height),
            file_preview_width=_to_missing(file.file_preview_width),
            file_encryption_algo=_to_missing(file.file_encryption_algo),
            chunk_size=_to_missing(file.chunk_size),
            caption=_to_missing(file.caption),
        )

    raise NotImplementedError(f"Unsupported attachment type: {attachment_type}")


def convert_async_file_to_domain(async_file: APIAsyncFile) -> File:
    attachment_type = convert_attachment_type_to_domain(async_file.type)

    if attachment_type == AttachmentTypes.IMAGE:
        async_file = cast(ApiAsyncFileImage, async_file)

        return Image(
            type=attachment_type,
            filename=async_file.file_name,
            size=async_file.file_size,
            is_async_file=True,
            _file_id=async_file.file_id,
            _file_mimetype=async_file.file_mime_type,
            _file_url=async_file.file,
            _file_hash=async_file.file_hash,
            file_preview=cast(str | None, _to_optional(async_file.file_preview)),
            file_preview_height=cast(
                int | None,
                _to_optional(async_file.file_preview_height),
            ),
            file_preview_width=cast(
                int | None,
                _to_optional(async_file.file_preview_width),
            ),
            file_encryption_algo=cast(
                str | None,
                _to_optional(async_file.file_encryption_algo),
            ),
            chunk_size=cast(int | None, _to_optional(async_file.chunk_size)),
            caption=cast(str | None, _to_optional(async_file.caption)),
        )

    if attachment_type == AttachmentTypes.VIDEO:
        async_file = cast(ApiAsyncFileVideo, async_file)

        return Video(
            type=attachment_type,
            filename=async_file.file_name,
            size=async_file.file_size,
            duration=async_file.duration,
            is_async_file=True,
            _file_id=async_file.file_id,
            _file_mimetype=async_file.file_mime_type,
            _file_url=async_file.file,
            _file_hash=async_file.file_hash,
            file_preview=cast(str | None, _to_optional(async_file.file_preview)),
            file_preview_height=cast(
                int | None,
                _to_optional(async_file.file_preview_height),
            ),
            file_preview_width=cast(
                int | None,
                _to_optional(async_file.file_preview_width),
            ),
            file_encryption_algo=cast(
                str | None,
                _to_optional(async_file.file_encryption_algo),
            ),
            chunk_size=cast(int | None, _to_optional(async_file.chunk_size)),
            caption=cast(str | None, _to_optional(async_file.caption)),
        )

    if attachment_type == AttachmentTypes.DOCUMENT:
        async_file = cast(ApiAsyncFileDocument, async_file)

        return Document(
            type=attachment_type,
            filename=async_file.file_name,
            size=async_file.file_size,
            is_async_file=True,
            _file_id=async_file.file_id,
            _file_mimetype=async_file.file_mime_type,
            _file_url=async_file.file,
            _file_hash=async_file.file_hash,
            file_preview=cast(str | None, _to_optional(async_file.file_preview)),
            file_preview_height=cast(
                int | None,
                _to_optional(async_file.file_preview_height),
            ),
            file_preview_width=cast(
                int | None,
                _to_optional(async_file.file_preview_width),
            ),
            file_encryption_algo=cast(
                str | None,
                _to_optional(async_file.file_encryption_algo),
            ),
            chunk_size=cast(int | None, _to_optional(async_file.chunk_size)),
            caption=cast(str | None, _to_optional(async_file.caption)),
        )

    if attachment_type == AttachmentTypes.VOICE:
        async_file = cast(ApiAsyncFileVoice, async_file)

        return Voice(
            type=attachment_type,
            filename=async_file.file_name,
            size=async_file.file_size,
            duration=async_file.duration,
            is_async_file=True,
            _file_id=async_file.file_id,
            _file_mimetype=async_file.file_mime_type,
            _file_url=async_file.file,
            _file_hash=async_file.file_hash,
            file_preview=cast(str | None, _to_optional(async_file.file_preview)),
            file_preview_height=cast(
                int | None,
                _to_optional(async_file.file_preview_height),
            ),
            file_preview_width=cast(
                int | None,
                _to_optional(async_file.file_preview_width),
            ),
            file_encryption_algo=cast(
                str | None,
                _to_optional(async_file.file_encryption_algo),
            ),
            chunk_size=cast(int | None, _to_optional(async_file.chunk_size)),
            caption=cast(str | None, _to_optional(async_file.caption)),
        )

    raise NotImplementedError(f"Unsupported attachment type: {attachment_type}")
