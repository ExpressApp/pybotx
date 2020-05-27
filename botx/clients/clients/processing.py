import collections
import contextlib
from typing import TypeVar

from httpx import Response
from pydantic import ValidationError

from botx import concurrency
from botx.clients.methods.base import APIResponse, BotXMethod, ErrorHandlersInMethod

ResponseT = TypeVar("ResponseT")


def extract_result(method: BotXMethod[ResponseT], response: Response) -> ResponseT:
    return_shape = method.__returning__
    api_response = APIResponse[return_shape].parse_obj(  # type: ignore
        response.json(),
    )
    result = api_response.result
    extractor = method.__result_extractor__
    if extractor is not None:
        # mypy does not understand that self passed here
        return extractor(result)  # type: ignore

    return result


async def handle_error(
    method: BotXMethod, error_handlers: ErrorHandlersInMethod, response: Response
) -> None:
    if not isinstance(error_handlers, collections.Sequence):
        error_handlers = [error_handlers]

    for error_handler in error_handlers:
        with contextlib.suppress(ValidationError):
            await concurrency.callable_to_coroutine(error_handler, method, response)
