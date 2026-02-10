from __future__ import annotations

from typing import Protocol
from os import PathLike
from typing import BinaryIO

from pybotx.domain.models.attachments import OutgoingAttachment
from pybotx.domain.ports.async_buffer import AsyncBufferReadable


class AttachmentFactoryPort(Protocol):
    async def from_path(
        self,
        path: str | PathLike[str],
        *,
        filename: str | None = None,
    ) -> OutgoingAttachment: ...  # pragma: no cover

    async def from_bytes(
        self,
        content: bytes,
        *,
        filename: str,
    ) -> OutgoingAttachment: ...  # pragma: no cover

    async def from_file(
        self,
        file: BinaryIO | AsyncBufferReadable,
        *,
        filename: str | None = None,
    ) -> OutgoingAttachment: ...  # pragma: no cover
