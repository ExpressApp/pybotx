"""Endpoints for chats resource."""

import json

from molten import Header, MultiPartParser, Request, RequestInput, Response, Settings

from botx.clients.methods.base import APIResponse
from botx.clients.methods.v3.files.download import DownloadFile
from botx.clients.methods.v3.files.upload import UploadFile
from botx.models.files import File, MetaFile
from botx.testing.botx_mock.binders import bind_implementation_to_method
from botx.testing.botx_mock.entities import create_test_metafile
from botx.testing.botx_mock.wsgi.messages import add_request_to_collection
from botx.testing.botx_mock.wsgi.responses import PydanticResponse


@bind_implementation_to_method(UploadFile)
def upload_file(request: Request, settings: Settings) -> Response:
    """Handle retrieving information about user request.

    Arguments:
        request: HTTP request from Molten.
        settings: application settings with storage.

    Returns:
        Response with metadata of file.
    """
    headers = dict(request.headers)
    form = MultiPartParser().parse(
        Header(headers["content-type"]),
        Header(headers["content-length"]),
        RequestInput(request.body_file),
    )

    meta = json.loads(form["meta"])  # type: ignore
    file = File.from_file(
        filename=form["content"].filename,  # type: ignore
        file=form["content"].stream,  # type: ignore
    )
    payload = UploadFile(
        group_chat_id=form["group_chat_id"],  # type: ignore
        file=file,
        meta=meta,
    )
    add_request_to_collection(settings, payload)
    return PydanticResponse(
        APIResponse[MetaFile](
            result=create_test_metafile(),
        ),
    )


@bind_implementation_to_method(DownloadFile)
def download_file(request: Request, settings: Settings) -> Response:
    """Handle retrieving information about user request.

    Arguments:
        request: HTTP request from Molten.
        settings: application settings with storage.

    Returns:
        Response with file content.
    """
    payload = DownloadFile.parse_obj(request.params)
    add_request_to_collection(settings, payload)
    return PydanticResponse(
        model=None,
        raw_data="content",
        headers={"Content-Type": "text/plain"},
    )
