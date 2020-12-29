"""Custom wrapper for HTTP request for BotX API."""
from typing import Any, Dict, Optional, Union

from pydantic import BaseModel

PrimitiveDataType = Union[None, str, int, float, bool]


class HTTPRequest(BaseModel):
    """Wrapper for HTTP request."""

    #: HTTP method.
    method: str

    #: URL for request.
    url: str

    #: headers for request.
    headers: Dict[str, str]

    #: query params for request.
    query_params: Dict[str, PrimitiveDataType]

    #: request body.
    request_data: Optional[Union[str, bytes]]


class HTTPResponse(BaseModel):
    """Wrapper for HTTP response."""

    #: response status code.
    status_code: int

    #: content
    bytes_body: bytes

    #: response json.
    json_body: Dict[str, Any]

    @property
    def is_successful(self) -> bool:
        """Is response status code successful.

        Returns:
           Check result.
        """
        return 200 <= self.status_code < 300  # noqa: WPS432
