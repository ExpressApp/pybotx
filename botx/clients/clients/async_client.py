from typing import List, Optional, Sequence, TypeVar

import httpx
from httpx import Response, StatusCode

from botx.clients.clients.processing import extract_result, handle_error
from botx.clients.methods.base import BotXMethod
from botx.exceptions import BotXAPIError
from botx.converters import optional_sequence_to_list

ResponseT = TypeVar("ResponseT")


class AsyncClient:
    def __init__(self, interceptors: Optional[Sequence] = None) -> None:
        self.http_client = httpx.AsyncClient()
        self.interceptors: List = optional_sequence_to_list(interceptors)

    async def call(
        self, method: BotXMethod[ResponseT], host: Optional[str] = None
    ) -> ResponseT:
        if host is not None:
            method.host = host

        response = await self.execute(method)

        if StatusCode.is_error(response.status_code):
            handlers_dict = method.__errors_handlers__
            error_handlers = handlers_dict.get(response.status_code)
            if error_handlers is not None:
                await handle_error(method, error_handlers, response)

            raise BotXAPIError(
                url=method.url,
                method=method.http_method,
                status=response.status_code,
                response_content=response.json(),
            )

        return extract_result(method, response)

    async def execute(self, method: BotXMethod) -> Response:
        request = method.build_http_request()
        return await self.http_client.request(
            request.method,
            request.url,
            headers=request.headers,
            params=request.query_params,
            data=request.request_data,
        )
