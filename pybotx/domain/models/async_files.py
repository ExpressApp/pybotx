from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import Literal
from collections.abc import AsyncGenerator
from uuid import UUID

from aiofiles.tempfile import SpooledTemporaryFile

from pybotx.domain.contextvars import bot_id_var, bot_var, chat_id_var
from pybotx.domain.constants import CHUNK_SIZE
from pybotx.domain.models.enums import AttachmentTypes


@dataclass(slots=True)
class AsyncFileBase:
    type: AttachmentTypes
    filename: str
    size: int

    is_async_file: Literal[True]

    _file_id: UUID
    _file_url: str
    _file_mimetype: str
    _file_hash: str
    file_preview: str | None = None
    file_preview_height: int | None = None
    file_preview_width: int | None = None
    file_encryption_algo: str | None = None
    chunk_size: int | None = None
    caption: str | None = None

    @property
    def file_url(self) -> str:
        return self._file_url

    @property
    def file_mimetype(self) -> str:
        return self._file_mimetype

    @property
    def file_hash(self) -> str:
        return self._file_hash

    @asynccontextmanager
    async def open(self, *, is_preview: bool = False) -> AsyncGenerator[SpooledTemporaryFile, None]:
        bot = bot_var.get()

        async with SpooledTemporaryFile(max_size=CHUNK_SIZE) as tmp_file:
            await bot.download_file(
                bot_id=bot_id_var.get(),
                chat_id=chat_id_var.get(),
                file_id=self._file_id,
                async_buffer=tmp_file,
                is_preview=is_preview,
            )

            yield tmp_file


@dataclass(slots=True)
class Image(AsyncFileBase):
    type: Literal[AttachmentTypes.IMAGE]


@dataclass(slots=True)
class Video(AsyncFileBase):
    type: Literal[AttachmentTypes.VIDEO]
    duration: int = 0


@dataclass(slots=True)
class Document(AsyncFileBase):
    type: Literal[AttachmentTypes.DOCUMENT]


@dataclass(slots=True)
class Voice(AsyncFileBase):
    type: Literal[AttachmentTypes.VOICE]
    duration: int = 0


File = Image | Video | Document | Voice
