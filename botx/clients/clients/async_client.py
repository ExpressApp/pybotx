"""Definition for async client for BotX API."""
from dataclasses import field
from typing import Any, List, Optional, TypeVar

import httpx
from httpx import Response
from loguru import logger
from pydantic.dataclasses import dataclass

from botx.clients.clients.processing import extract_result, handle_error
from botx.clients.methods.base import BotXMethod
from botx.converters import optional_sequence_to_list
from botx.exceptions import BotXAPIError
from botx.shared import BotXDataclassConfig, debug_bot_id_var

ResponseT = TypeVar("ResponseT")


@dataclass(config=BotXDataclassConfig)
class AsyncClient:
    """Async client for BotX API."""

    http_client: httpx.AsyncClient = field(init=False)
    interceptors: List[Any] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Init or update special fields."""
        self.http_client = httpx.AsyncClient()
        self.interceptors = optional_sequence_to_list(self.interceptors)

    async def call(
        self, method: BotXMethod[ResponseT], host: Optional[str] = None,
    ) -> ResponseT:
        """Make request to BotX API using passed method and return result.

        Arguments:
            method: BotX API method that should be called.
            host: override for host from method.

        Returns:
            Shape specified for method response.

        Raises:
            BotXAPIError: raised if handler for error status code was not found.
        """
        if host is not None:
            method.host = host

        response = await self.execute(method)

        if httpx.codes.is_error(response.status_code):
            handlers_dict = method.error_handlers
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
        """Make real HTTP request using client.

        Arguments:
            method: BotX API method that should be called.

        Returns:
            HTTP response from API.
        """
        request = method.build_http_request()
        method_name = method.__repr_name__()  # noqa: WPS609
        logger.bind(botx_client=True, payload=request.to_dict()).debug(
            "send {0} request to bot {1}", method_name, debug_bot_id_var.get(),
        )
        return await self.http_client.request(
            request.method,
            request.url,
            headers=request.headers,
            params=request.query_params,
            content=request.request_data,
        )
