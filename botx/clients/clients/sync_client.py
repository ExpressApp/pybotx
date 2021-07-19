"""Definition for sync client for BotX API."""
from dataclasses import field
from http import HTTPStatus
from json import JSONDecodeError
from typing import Any, List, TypeVar

import httpx
from pydantic.dataclasses import dataclass

from botx import concurrency
from botx.clients.clients.processing import extract_result, handle_error
from botx.clients.methods.base import BotXMethod, ErrorHandlersInMethod
from botx.clients.types.http import HTTPRequest, HTTPResponse
from botx.converters import optional_sequence_to_list
from botx.exceptions import (
    BotXAPIError,
    BotXAPIRouteDeprecated,
    BotXConnectError,
    BotXJSONDecodeError,
)
from botx.shared import BotXDataclassConfig

ResponseT = TypeVar("ResponseT")


@dataclass(config=BotXDataclassConfig)
class Client:
    """Sync client for BotX API."""

    http_client: httpx.Client = field(init=False)
    interceptors: List[Any] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Init or update special fields."""
        self.http_client = httpx.Client()
        self.interceptors = optional_sequence_to_list(self.interceptors)

    @classmethod
    def build_request(cls, method: BotXMethod[ResponseT]) -> HTTPRequest:
        """Build HTTPRequest from passed BotX method.

        Arguments:
            method: BotX method.

        Returns:
            Built request.
        """
        return method.build_http_request()

    def process_response(
        self,
        method: BotXMethod[ResponseT],
        response: HTTPResponse,
    ) -> ResponseT:
        """Handle errors and extract data from BotX API response.

        Arguments:
            method: BotX API method.
            response: HTTPResponse that is result of method executing.

        Returns:
            Shape specified for method response.

        Raises:
            BotXAPIError: raised if handler for error status code was not found.
            BotXAPIRouteDeprecated: raised if API route was deprecated.
        """
        if response.is_error or response.is_redirect:
            handlers_dict = method.error_handlers
            error_handlers = handlers_dict.get(response.status_code)
            if error_handlers is not None:
                _handle_error(method, error_handlers, response)

            if response.status_code == HTTPStatus.GONE:
                raise BotXAPIRouteDeprecated(
                    url=method.url,
                    method=method.http_method,
                    status=response.status_code,
                    response_content=response.json_body,
                )

            raise BotXAPIError(
                url=method.url,
                method=method.http_method,
                status=response.status_code,
                response_content=response.json_body,
            )

        return extract_result(method, response)

    def execute(self, request: HTTPRequest) -> HTTPResponse:
        """Make request to BotX API.

        Arguments:
            request: HTTPRequest that was built from method.

        Returns:
            HTTP response from API.

        Raises:
            BotXConnectError: raised if unable to connect to service.
            BotXJSONDecodeError: raised if service returned invalid body.
        """
        try:
            response = self.http_client.request(
                request.method,
                request.url,
                headers=request.headers,
                params=request.query_params,
                json=request.json_body,
            )
        except httpx.HTTPError as httpx_exc:
            raise BotXConnectError(
                url=request.url,
                method=request.method,
            ) from httpx_exc

        try:
            json_body = response.json()
        except JSONDecodeError as exc:
            raise BotXJSONDecodeError(url=request.url, method=request.method) from exc

        return HTTPResponse(
            status_code=response.status_code,
            json_body=json_body,
        )


def _handle_error(
    method: BotXMethod,
    error_handlers: ErrorHandlersInMethod,
    response: HTTPResponse,
) -> None:
    concurrency.async_to_sync(handle_error)(method, error_handlers, response)
