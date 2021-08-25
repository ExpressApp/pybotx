"""Method for uploading file to chat."""
from http import HTTPStatus
from typing import Dict
from uuid import UUID

from botx.clients.methods.base import AuthorizedBotXMethod
from botx.clients.methods.errors.files import chat_not_found
from botx.clients.types.http import HTTPRequest
from botx.clients.types.upload_file import UploadingFileMeta
from botx.models.files import File, MetaFile


class UploadFile(AuthorizedBotXMethod[MetaFile]):
    """Method for uploading file to a chat."""

    __url__ = "/api/v3/botx/files/upload"
    __method__ = "POST"
    __returning__ = MetaFile
    __errors_handlers__ = {
        HTTPStatus.NOT_FOUND: (chat_not_found.handle_error,),
    }

    #: ID of the chat.
    group_chat_id: UUID

    #: file for uploading.
    file: File

    #: file metadata.
    meta: UploadingFileMeta

    @property
    def headers(self) -> Dict[str, str]:
        """Headers that should be used in request."""
        headers = super().headers
        # used to enable the client to attach a Content-Type with a boundary
        headers.pop("Content-Type")
        return headers

    def build_http_request(self) -> HTTPRequest:
        """Build HTTP request that can be used by clients for making real requests.

        Returns:
            Built HTTP request.
        """
        files = {"content": (self.file.file_name, self.file.file)}
        request_data = {
            "group_chat_id": str(self.group_chat_id),
            "meta": self.meta.json(),
        }

        return HTTPRequest(
            method=self.http_method,
            url=self.url,
            headers=self.headers,
            query_params=self.query_params,
            json_body={},
            data=request_data,
            files=files,  # type: ignore
        )
