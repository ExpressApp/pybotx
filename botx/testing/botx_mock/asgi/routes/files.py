"""Endpoints for chats resource."""

import json

from starlette.requests import Request
from starlette.responses import Response

from botx.clients.methods.base import APIResponse
from botx.clients.methods.v3.files.download import DownloadFile
from botx.clients.methods.v3.files.upload import UploadFile
from botx.models.files import File, MetaFile
from botx.testing.botx_mock.asgi.messages import add_request_to_collection
from botx.testing.botx_mock.asgi.responses import PydanticResponse
from botx.testing.botx_mock.binders import bind_implementation_to_method
from botx.testing.botx_mock.entities import create_test_metafile


@bind_implementation_to_method(UploadFile)
async def upload_file(request: Request) -> Response:
    """Handle retrieving information about user request.

    Arguments:
        request: HTTP request from Starlette.

    Returns:
        Response with metadata of file.
    """
    form = dict(await request.form())
    meta = json.loads(form["meta"])
    filename = form["content"].filename  # type: ignore
    file = File.from_file(
        filename=filename,
        file=form["content"].file,  # type: ignore
    )
    payload = UploadFile(
        group_chat_id=form["group_chat_id"],  # type: ignore
        file=file,
        meta=meta,
    )
    add_request_to_collection(request, payload)
    return PydanticResponse(
        APIResponse[MetaFile](
            result=create_test_metafile(filename),
        ),
    )


@bind_implementation_to_method(DownloadFile)
async def download_file(request: Request) -> Response:
    """Handle retrieving information about user request.

    Arguments:
        request: HTTP request from Starlette.

    Returns:
        Response with file content.
    """
    payload = DownloadFile.parse_obj(request.query_params)
    add_request_to_collection(request, payload)
    return PydanticResponse(model=None, raw_data=b"content", media_type="text/plain")
