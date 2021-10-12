import tempfile
from typing import Literal, Optional
from uuid import UUID

from botx.client.authorized_botx_method import AuthorizedBotXMethod
from botx.client.files_api.download_file import (
    AsyncBufferReadable,
    get_async_buffer_filename,
)
from botx.constants import CHUNK_SIZE
from botx.shared_models.api.async_files import APIAsyncFile
from botx.shared_models.api_base import (
    UnverifiedPayloadBaseModel,
    VerifiedPayloadBaseModel,
)


class BotXAPIUploadFileMeta(UnverifiedPayloadBaseModel):
    duration: Optional[int] = None
    caption: Optional[str] = None


class BotXAPIUploadFileRequestPayload(UnverifiedPayloadBaseModel):
    group_chat_id: UUID
    meta: str

    @classmethod
    def from_domain(
        cls,
        chat_id: UUID,
        duration: Optional[int] = None,
        caption: Optional[str] = None,
    ) -> "BotXAPIUploadFileRequestPayload":
        return cls(
            group_chat_id=chat_id,
            meta=BotXAPIUploadFileMeta(
                duration=duration,
                caption=caption,
            ).json(),
        )


class BotXAPIUploadFileResponsePayload(VerifiedPayloadBaseModel):
    result: APIAsyncFile
    status: Literal["ok"]


class UploadFileMethod(AuthorizedBotXMethod):
    async def execute(
        self,
        payload: BotXAPIUploadFileRequestPayload,
        async_buffer: AsyncBufferReadable,
        filename: Optional[str],
    ) -> BotXAPIUploadFileResponsePayload:
        path = "/api/v3/botx/files/upload"

        if not filename:
            filename = get_async_buffer_filename(async_buffer)

        with tempfile.SpooledTemporaryFile(max_size=CHUNK_SIZE) as tmp_file:
            chunk = await async_buffer.read(CHUNK_SIZE)
            while chunk:
                tmp_file.write(chunk)
                chunk = await async_buffer.read(CHUNK_SIZE)

            tmp_file.seek(0)

            response = await self._botx_method_call(
                "POST",
                self._build_url(path),
                data=payload.jsonable_dict(),
                files={"content": (filename, tmp_file)},
            )

        return self._extract_api_model(
            BotXAPIUploadFileResponsePayload,
            response,
        )
