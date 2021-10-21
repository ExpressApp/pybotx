from uuid import UUID

from botx.client.authorized_botx_method import AuthorizedBotXMethod
from botx.shared_models.api_base import UnverifiedPayloadBaseModel
from botx.shared_models.async_buffer import AsyncBufferWritable


class BotXAPIDownloadFileRequestPayload(UnverifiedPayloadBaseModel):
    group_chat_id: UUID
    file_id: UUID
    is_preview: bool

    @classmethod
    def from_domain(
        cls,
        chat_id: UUID,
        file_id: UUID,
    ) -> "BotXAPIDownloadFileRequestPayload":
        return cls(
            group_chat_id=chat_id,
            file_id=file_id,
            is_preview=False,
        )


class DownloadFileMethod(AuthorizedBotXMethod):
    status_handlers = {
        **AuthorizedBotXMethod.status_handlers,
        # TODO: find a way to catch errors in streaming response
    }

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
