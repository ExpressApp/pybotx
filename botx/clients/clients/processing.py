"""Logic for handling response from BotX API for real HTTP responses."""
import collections
import contextlib
from io import BytesIO
from typing import TypeVar

from pydantic import ValidationError

from botx import concurrency
from botx.clients.methods.base import APIResponse, BotXMethod, ErrorHandlersInMethod
from botx.clients.types.http import ExpectedType, HTTPResponse
from botx.models.files import File

ResponseT = TypeVar("ResponseT")


def build_file(response: HTTPResponse) -> File:
    """Build file from response raw data.

    Arguments:
        response: HTTP response from BotX API.

    Returns:
        Built file from response.
    """
    mimetype = response.headers["content-type"].split(";", 1)[0]
    ext = File.get_ext_by_mimetype(mimetype)
    file_name = "document{0}".format(ext)
    return File.from_file(BytesIO(response.raw_data), file_name)  # type: ignore


def extract_result(  # noqa: WPS210
    method: BotXMethod[ResponseT],
    response: HTTPResponse,
) -> ResponseT:
    """Extract result from successful response and convert it to right shape.

    Arguments:
        method: method to BotX API that was called.
        response: HTTP response from BotX API.

    Returns:
        Converted shape from BotX API.
    """
    if method.expected_type == ExpectedType.BINARY:
        return build_file(response)  # type: ignore

    return_shape = method.returning
    api_response = APIResponse[return_shape].parse_obj(  # type: ignore
        response.json_body,
    )
    response_result = api_response.result
    extractor = method.result_extractor
    if extractor is not None:
        # mypy does not understand that self passed here
        return extractor(response_result)  # type: ignore

    return response_result


async def handle_error(
    method: BotXMethod,
    error_handlers: ErrorHandlersInMethod,
    response: HTTPResponse,
) -> None:
    """Handle error status code from BotX API.

    Arguments:
        method: method to BotX API that was called.
        error_handlers: registered on method handlers for different responses.
        response: HTTP response from BotX API.
    """
    if not isinstance(error_handlers, collections.Sequence):
        error_handlers = [error_handlers]

    for error_handler in error_handlers:
        with contextlib.suppress(ValidationError):
            await concurrency.callable_to_coroutine(error_handler, method, response)
