from __future__ import annotations

from typing import Protocol, runtime_checkable
from uuid import UUID

from pybotx.domain.ports.async_buffer import AsyncBufferWritable


@runtime_checkable
class BotAccessPort(Protocol):
    async def download_file(
        self,
        *,
        bot_id: UUID,
        chat_id: UUID,
        file_id: UUID,
        async_buffer: AsyncBufferWritable,
        is_preview: bool = False,
    ) -> None: ...  # pragma: no cover

    async def download_url(
        self,
        *,
        url: str,
        async_buffer: AsyncBufferWritable,
    ) -> None: ...  # pragma: no cover
