from __future__ import annotations

from os import PathLike
from typing import BinaryIO

from pybotx.domain.models.attachments import OutgoingAttachment
from pybotx.domain.ports.async_buffer import AsyncBufferReadable
from pybotx.domain.ports.attachment_factory import AttachmentFactoryPort


class AttachmentFactory:
    def __init__(self, factory: AttachmentFactoryPort) -> None:
        self._factory = factory

    async def from_path(
        self,
        path: str | PathLike[str],
        *,
        filename: str | None = None,
    ) -> OutgoingAttachment:
        return await self._factory.from_path(path, filename=filename)

    async def from_bytes(
        self,
        content: bytes,
        *,
        filename: str,
    ) -> OutgoingAttachment:
        return await self._factory.from_bytes(content, filename=filename)

    async def from_file(
        self,
        file: BinaryIO | AsyncBufferReadable,
        *,
        filename: str | None = None,
    ) -> OutgoingAttachment:
        return await self._factory.from_file(file, filename=filename)


__all__ = ("AttachmentFactory",)
