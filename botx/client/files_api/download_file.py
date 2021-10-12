from pathlib import Path
from typing import Optional, Protocol, Union
from uuid import UUID

from botx.client.authorized_botx_method import AuthorizedBotXMethod
from botx.shared_models.api_base import UnverifiedPayloadBaseModel


class AsyncBufferBase(Protocol):  # TODO: Move up
    name: str

    async def seek(self, cursor: int) -> int:
        ...  # noqa: WPS428


class AsyncBufferWritable(AsyncBufferBase):
    async def write(self, content: bytes) -> int:
        ...  # noqa: WPS428


class AsyncBufferReadable(AsyncBufferBase):
    async def read(self, n: Optional[int] = None) -> bytes:
        ...  # noqa: WPS428


def get_async_buffer_filename(
    async_buffer: Union[AsyncBufferReadable, AsyncBufferWritable],
) -> str:
    return Path(async_buffer.name).name


class BotXAPIDownloadFileRequestPayload(UnverifiedPayloadBaseModel):
    group_chat_id: UUID
    file_id: UUID
    is_preview: bool

    @classmethod
    def from_domain(
        cls,
        chat_id: UUID,
        file_id: UUID,
        download_preview: bool = False,
    ) -> "BotXAPIDownloadFileRequestPayload":
        return cls(
            group_chat_id=chat_id,
            file_id=file_id,
            is_preview=download_preview,
        )


class DownloadFileMethod(AuthorizedBotXMethod):
    async def execute(
        self,
        payload: BotXAPIDownloadFileRequestPayload,
        async_buffer: AsyncBufferWritable,
    ) -> None:
        path = "/api/v3/botx/files/download"

        async with self._botx_method_stream(
            "GET",
            self._build_url(path),
            params=payload.jsonable_dict(),
        ) as response:
            async for chunk in response.aiter_bytes():
                await async_buffer.write(chunk)

        await async_buffer.seek(0)
