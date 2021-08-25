"""Mixin for shortcut for files resource requests."""

from typing import Optional
from uuid import UUID

from botx.bots.mixins.requests.call_protocol import BotXMethodCallProtocol
from botx.clients.clients.async_client import AsyncClient
from botx.clients.methods.v3.files.download import DownloadFile
from botx.clients.methods.v3.files.upload import UploadFile
from botx.clients.types.upload_file import UploadingFileMeta
from botx.models.files import File, MetaFile
from botx.models.messages.sending.credentials import SendingCredentials


class FilesRequestsMixin:
    """Mixin for shortcut for files resource requests."""

    client: AsyncClient

    async def upload_file(  # noqa: WPS211
        self: BotXMethodCallProtocol,
        credentials: SendingCredentials,
        sending_file: File,
        group_chat_id: UUID,
        *,
        duration: Optional[int] = None,
        caption: Optional[str] = None,
    ) -> MetaFile:
        """Upload file to the chat.

        Arguments:
            credentials: credentials for making request.
            sending_file: file to upload.
            group_chat_id: ID of the chat that accepts the file.
            duration: duration of the voice or the video.
            caption: file caption.

        Returns:
            File metadata.
        """
        return await self.call_method(
            UploadFile(
                group_chat_id=group_chat_id,
                file=sending_file,
                meta=UploadingFileMeta(
                    duration=duration,
                    caption=caption,
                ),
            ),
            credentials=credentials,
        )

    async def download_file(
        self: BotXMethodCallProtocol,
        credentials: SendingCredentials,
        file_id: UUID,
        group_chat_id: UUID,
        *,
        is_preview: bool = False,
    ) -> File:
        """Download file from the chat.

        Arguments:
            credentials: credentials for making request.
            file_id: ID of the file.
            group_chat_id: ID of the chat that accepts the file.
            is_preview: get preview or file.

        Returns:
            Downloaded file.
        """
        return await self.call_method(
            DownloadFile(
                file_id=file_id,
                group_chat_id=group_chat_id,
                is_preview=is_preview,
            ),
            credentials=credentials,
        )
