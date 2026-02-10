from __future__ import annotations

from uuid import UUID

from pybotx.domain.missing import Missing, Undefined
from pybotx.domain.models.async_files import File
from pybotx.domain.ports.async_buffer import AsyncBufferReadable, AsyncBufferWritable


class BotFilesMixin:
    async def download_file(
        self,
        *,
        bot_id: UUID,
        chat_id: UUID,
        file_id: UUID,
        async_buffer: AsyncBufferWritable,
        is_preview: bool = False,
    ) -> None:
        """Download file form file service.

        :param bot_id: Bot which should perform the request.
        :param chat_id: Target chat id.
        :param file_id: Async file id.
        :param async_buffer: Buffer to write downloaded file.
        :param is_preview: If true and file has preview, return it instead of original.
        """
        await self._botx_api.download_file(
            bot_id=bot_id,
            chat_id=chat_id,
            file_id=file_id,
            async_buffer=async_buffer,
            is_preview=is_preview,
        )

    async def download_url(
        self,
        *,
        url: str,
        async_buffer: AsyncBufferWritable,
    ) -> None:
        """Download an arbitrary URL into the provided buffer."""
        await self._botx_api.download_url(url=url, async_buffer=async_buffer)

    async def upload_file(
        self,
        *,
        bot_id: UUID,
        chat_id: UUID,
        async_buffer: AsyncBufferReadable,
        filename: str,
        duration: Missing[int] = Undefined,
        caption: Missing[str] = Undefined,
    ) -> File:
        """Upload file to file service.

        :param bot_id: Bot which should perform the request.
        :param chat_id: Target chat id.
        :param async_buffer: Buffer to write downloaded file.
        :param filename: File name.
        :param duration: Video duration.
        :param caption: Text under file.

        :return: Meta info of uploaded file.
        """
        return await self._botx_api.upload_file(
            bot_id=bot_id,
            chat_id=chat_id,
            async_buffer=async_buffer,
            filename=filename,
            duration=duration,
            caption=caption,
        )
