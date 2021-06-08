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
    json_body: Optional[Dict[str, Any]]


class HTTPResponse(BaseModel):
    """Wrapper for HTTP response."""

    #: response status code.
    status_code: int

    #: response body.
    json_body: Dict[str, Any]

    @property
    def is_redirect(self) -> bool:
        """Is redirect status code.

        Returns:
           Check result.
        """
        return 300 <= self.status_code < 399  # noqa: WPS432

    @property
    def is_error(self) -> bool:
        """Is error status code.

        Returns:
           Check result.
        """
        return 400 <= self.status_code < 599  # noqa: WPS432
