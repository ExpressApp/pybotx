"""Method for downloading file from chat."""
from http import HTTPStatus
from uuid import UUID

from botx.clients.methods.base import AuthorizedBotXMethod
from botx.clients.methods.errors.files import (
    chat_not_found,
    file_deleted,
    metadata_not_found,
    without_preview,
)
from botx.clients.types.http import ExpectedType, HTTPRequest
from botx.models.files import File


class DownloadFile(AuthorizedBotXMethod[File]):
    """Method for downloading a file from chat."""

    __url__ = "/api/v3/botx/files/download"
    __method__ = "GET"
    __returning__ = File
    __expected_type__ = ExpectedType.BINARY
    __errors_handlers__ = {
        HTTPStatus.NO_CONTENT: (file_deleted.handle_error,),
        HTTPStatus.BAD_REQUEST: (without_preview.handle_error,),
        HTTPStatus.NOT_FOUND: (
            chat_not_found.handle_error,
            metadata_not_found.handle_error,
        ),
    }

    #: ID of the chat with file.
    group_chat_id: UUID

    #: ID of the file for downloading.
    file_id: UUID

    #: preview or file.
    is_preview: bool

    def build_http_request(self) -> HTTPRequest:
        """Build HTTP request that can be used by clients for making real requests.

        Returns:
            Built HTTP request.
        """
        request_params = self.build_serialized_dict()

        return HTTPRequest.construct(
            method=self.http_method,
            url=self.url,
            headers=self.headers,
            query_params=dict(request_params),  # type: ignore
            json_body={},
            expected_type=self.expected_type,
            should_process_as_error=[HTTPStatus.NO_CONTENT],
        )
