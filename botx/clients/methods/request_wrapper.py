"""Custom wrapper for HTTP request for BotX API."""
from typing import Dict, Optional, Union

from pydantic.dataclasses import dataclass

PrimitiveDataType = Union[None, str, int, float, bool]


@dataclass
class HTTPRequest:
    """Wrapper for HTTP request."""

    #: HTTP method.
    method: str

    #: URL for request.
    url: str

    #: headers for request
    headers: Dict[str, str]

    #: query params for request.
    query_params: Dict[str, PrimitiveDataType]

    #: request body.
    request_data: Optional[Union[str, bytes]]

    def to_dict(self) -> dict:
        """Convert request to dictionary.

        Returns:
            Built dictionary.
        """
        return {
            "method": self.method,
            "url": self.url,
            "headers": self.headers,
            "query_params": self.query_params,
            "request_data": self.request_data,
        }
