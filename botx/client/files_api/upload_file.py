import tempfile
from uuid import UUID

from botx.async_buffer import AsyncBufferReadable
from botx.client.authorized_botx_method import AuthorizedBotXMethod
from botx.client.botx_method import response_exception_thrower
from botx.client.exceptions.common import ChatNotFoundError
from botx.constants import CHUNK_SIZE
from botx.missing import Missing
from botx.models.api_base import UnverifiedPayloadBaseModel, VerifiedPayloadBaseModel
from botx.models.async_files import APIAsyncFile, File, convert_async_file_to_domain

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal  # type: ignore  # noqa: WPS440


class BotXAPIUploadFileMeta(UnverifiedPayloadBaseModel):
    duration: Missing[int]
    caption: Missing[str]


class BotXAPIUploadFileRequestPayload(UnverifiedPayloadBaseModel):
    group_chat_id: UUID
    meta: str

    @classmethod
    def from_domain(
        cls,
        chat_id: UUID,
        duration: Missing[int],
        caption: Missing[str],
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

    def to_domain(self) -> File:
        return convert_async_file_to_domain(self.result)


class UploadFileMethod(AuthorizedBotXMethod):
    status_handlers = {
        **AuthorizedBotXMethod.status_handlers,
        404: response_exception_thrower(ChatNotFoundError),
    }

    async def execute(
        self,
        payload: BotXAPIUploadFileRequestPayload,
        async_buffer: AsyncBufferReadable,
        filename: str,
    ) -> BotXAPIUploadFileResponsePayload:
        path = "/api/v3/botx/files/upload"

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

        return self._verify_and_extract_api_model(
            BotXAPIUploadFileResponsePayload,
            response,
        )
