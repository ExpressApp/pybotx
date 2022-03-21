from typing import NoReturn
from uuid import UUID

import httpx

from botx.async_buffer import AsyncBufferWritable
from botx.client.authorized_botx_method import AuthorizedBotXMethod
from botx.client.botx_method import response_exception_thrower
from botx.client.exceptions.common import ChatNotFoundError
from botx.client.exceptions.files import FileDeletedError, FileMetadataNotFound
from botx.client.exceptions.http import InvalidBotXStatusCodeError
from botx.models.api_base import UnverifiedPayloadBaseModel


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


def not_found_error_handler(response: httpx.Response) -> NoReturn:
    reason = response.json().get("reason")

    if reason == "file_metadata_not_found":
        raise FileMetadataNotFound.from_response(response)
    elif reason == "chat_not_found":
        raise ChatNotFoundError.from_response(response)

    raise InvalidBotXStatusCodeError(response)


class DownloadFileMethod(AuthorizedBotXMethod):
    status_handlers = {
        **AuthorizedBotXMethod.status_handlers,
        204: response_exception_thrower(FileDeletedError),
        404: not_found_error_handler,
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
            # https://github.com/nedbat/coveragepy/issues/1223
            async for chunk in response.aiter_bytes():  # pragma: no cover
                await async_buffer.write(chunk)

        await async_buffer.seek(0)
