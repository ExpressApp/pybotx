from typing import List, Optional, Sequence, TypeVar

import httpx
from httpx import Response, StatusCode

from botx import concurrency
from botx.clients.clients.processing import extract_result, handle_error
from botx.clients.methods.base import BotXMethod, ErrorHandlersInMethod
from botx.exceptions import BotXAPIError
from botx.utils import optional_sequence_to_list

ResponseT = TypeVar("ResponseT")


class Client:
    def __init__(self, interceptors: Optional[Sequence] = None) -> None:
        self.http_client = httpx.Client()
        self.interceptors: List = optional_sequence_to_list(interceptors)

    def call(
        self, method: BotXMethod[ResponseT], host: Optional[str] = None
    ) -> ResponseT:
        if host is not None:
            method.host = host

        response = self.execute(method)

        if StatusCode.is_error(response.status_code):
            handlers_dict = method.__errors_handlers__  # noqa: WPS609
            error_handlers = handlers_dict.get(response.status_code)
            if error_handlers is not None:
                _handle_error(method, error_handlers, response)

            raise BotXAPIError(
                url=method.url,
                method=method.http_method,
                status=response.status_code,
                response_content=response.json(),
            )

        return extract_result(method, response)

    def execute(self, method: BotXMethod) -> Response:
        request = method.build_http_request()
        return self.http_client.request(
            request.method,
            request.url,
            headers=request.headers,  # type: ignore
            params=request.query_params,
            data=request.request_data,
        )


def _handle_error(
    method: BotXMethod, error_handlers: ErrorHandlersInMethod, response: Response
) -> None:
    concurrency.async_to_sync(handle_error)(method, error_handlers, response)
