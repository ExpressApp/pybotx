from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import AsyncGenerator, Union, cast
from uuid import UUID

from aiofiles.tempfile import SpooledTemporaryFile

from botx.bot.contextvars import bot_id_var, bot_var, chat_id_var
from botx.constants import CHUNK_SIZE
from botx.models.api_base import VerifiedPayloadBaseModel
from botx.models.enums import (
    APIAttachmentTypes,
    AttachmentTypes,
    convert_attachment_type_to_domain,
)

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal  # type: ignore  # noqa: WPS440


@dataclass
class AsyncFileBase:
    type: AttachmentTypes
    filename: str
    size: int

    is_async_file: Literal[True]

    _file_id: UUID

    @asynccontextmanager
    async def open(self) -> AsyncGenerator[SpooledTemporaryFile, None]:
        bot = bot_var.get()

        async with SpooledTemporaryFile(max_size=CHUNK_SIZE) as tmp_file:
            await bot.download_file(
                bot_id=bot_id_var.get(),
                chat_id=chat_id_var.get(),
                file_id=self._file_id,
                async_buffer=tmp_file,
            )

            yield tmp_file


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
    file_id: UUID
    file_name: str
    file_size: int

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


def convert_async_file_to_file(async_file: APIAsyncFile) -> File:
    attachment_type = convert_attachment_type_to_domain(async_file.type)

    if attachment_type == AttachmentTypes.IMAGE:
        attachment_type = cast(Literal[AttachmentTypes.IMAGE], attachment_type)
        async_file = cast(ApiAsyncFileImage, async_file)

        return Image(
            type=attachment_type,
            filename=async_file.file_name,
            size=async_file.file_size,
            is_async_file=True,
            _file_id=async_file.file_id,
        )

    if attachment_type == AttachmentTypes.VIDEO:
        attachment_type = cast(Literal[AttachmentTypes.VIDEO], attachment_type)
        async_file = cast(ApiAsyncFileVideo, async_file)

        return Video(
            type=attachment_type,
            filename=async_file.file_name,
            size=async_file.file_size,
            duration=async_file.duration,
            is_async_file=True,
            _file_id=async_file.file_id,
        )

    if attachment_type == AttachmentTypes.DOCUMENT:
        attachment_type = cast(Literal[AttachmentTypes.DOCUMENT], attachment_type)
        async_file = cast(ApiAsyncFileDocument, async_file)

        return Document(
            type=attachment_type,
            filename=async_file.file_name,
            size=async_file.file_size,
            is_async_file=True,
            _file_id=async_file.file_id,
        )

    if attachment_type == AttachmentTypes.VOICE:
        attachment_type = cast(Literal[AttachmentTypes.VOICE], attachment_type)
        async_file = cast(ApiAsyncFileVoice, async_file)

        return Voice(
            type=attachment_type,
            filename=async_file.file_name,
            size=async_file.file_size,
            duration=async_file.duration,
            is_async_file=True,
            _file_id=async_file.file_id,
        )

    raise NotImplementedError(f"Unsupported attachment type: {attachment_type}")
