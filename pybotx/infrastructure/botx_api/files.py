from __future__ import annotations

from uuid import UUID

from pybotx.domain.errors import TransportError
from pybotx.domain.ports.async_buffer import AsyncBufferReadable, AsyncBufferWritable
from pybotx.domain.ports.http_client import HttpClientError, HttpRequest
from pybotx.domain.models.async_files import File
from pybotx.domain.missing import Missing, Undefined
from pybotx.infrastructure.client.files_api.download_file import (
    BotXAPIDownloadFileRequestPayload,
    DownloadFileMethod,
)
from pybotx.infrastructure.client.files_api.upload_file import (
    BotXAPIUploadFileRequestPayload,
    UploadFileMethod,
)


class FilesApiMixin:
    async def download_file(
        self,
        *,
        bot_id: UUID,
        chat_id: UUID,
        file_id: UUID,
        async_buffer: AsyncBufferWritable,
        is_preview: bool = False,
    ) -> None:
        method = self._method_factory.build(DownloadFileMethod, bot_id=bot_id)
        payload = BotXAPIDownloadFileRequestPayload.from_domain(
            chat_id=chat_id,
            file_id=file_id,
            is_preview=is_preview,
        )
        await method.execute(payload, async_buffer)

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
        method = self._method_factory.build(UploadFileMethod, bot_id=bot_id)
        payload = BotXAPIUploadFileRequestPayload.from_domain(
            chat_id=chat_id,
            duration=duration,
            caption=caption,
        )
        botx_api_async_file = await method.execute(payload, async_buffer, filename)
        return botx_api_async_file.to_domain()

    async def download_url(
        self,
        *,
        url: str,
        async_buffer: AsyncBufferWritable,
    ) -> None:
        try:
            response = await self._http_client.send(
                HttpRequest(method="GET", url=url),
            )
            response.raise_for_status()
        except HttpClientError as exc:
            raise TransportError(str(exc)) from exc
        await async_buffer.write(response.content)
        await async_buffer.seek(0)
