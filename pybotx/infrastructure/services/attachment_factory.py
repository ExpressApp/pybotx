from __future__ import annotations

import asyncio
import inspect
from os import PathLike
from pathlib import Path
from typing import BinaryIO

import aiofiles

from pybotx.domain.models.attachments import OutgoingAttachment
from pybotx.domain.ports.async_buffer import AsyncBufferReadable
from pybotx.domain.ports.attachment_factory import AttachmentFactoryPort


class AttachmentFactory(AttachmentFactoryPort):
    async def from_path(
        self,
        path: str | PathLike[str],
        *,
        filename: str | None = None,
    ) -> OutgoingAttachment:
        file_path = Path(path)
        async with aiofiles.open(file_path, "rb") as handle:
            content = await handle.read()

        return OutgoingAttachment(
            content=content,
            filename=filename or file_path.name,
        )

    async def from_bytes(
        self,
        content: bytes,
        *,
        filename: str,
    ) -> OutgoingAttachment:
        return OutgoingAttachment(content=content, filename=filename)

    async def from_file(
        self,
        file: BinaryIO | AsyncBufferReadable,
        *,
        filename: str | None = None,
    ) -> OutgoingAttachment:
        inferred_name = filename
        if inferred_name is None and hasattr(file, "name"):
            inferred_name = Path(str(getattr(file, "name"))).name

        read_attr = getattr(file, "read", None)
        if read_attr is None:
            raise TypeError("file object has no read method")

        if inspect.iscoroutinefunction(read_attr):
            content = await read_attr()
        else:
            content = await asyncio.to_thread(read_attr)

        if inferred_name is None:
            raise ValueError("filename is required for files without a name")

        return OutgoingAttachment(content=content, filename=inferred_name)


__all__ = ("AttachmentFactory",)
