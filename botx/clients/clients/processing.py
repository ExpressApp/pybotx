"""Logic for handling response from BotX API for real HTTP responses."""
import collections
import contextlib
from typing import TypeVar

from httpx import Response
from pydantic import ValidationError

from botx import concurrency
from botx.clients.methods.base import APIResponse, BotXMethod, ErrorHandlersInMethod

ResponseT = TypeVar("ResponseT")


def extract_result(method: BotXMethod[ResponseT], response: Response) -> ResponseT:
    """Extract result from successful response and convert it to right shape.

    Arguments:
        method: method to BotX API that was called.
        response: HTTP response from BotX API.

    Returns:
        Converted shape from BotX API.
    """
    return_shape = method.returning
    api_response = APIResponse[return_shape].parse_obj(response.json())  # type: ignore
    response_result = api_response.result
    extractor = method.result_extractor
    if extractor is not None:
        # mypy does not understand that self passed here
        return extractor(response_result)  # type: ignore

    return response_result


async def handle_error(
    method: BotXMethod, error_handlers: ErrorHandlersInMethod, response: Response,
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
