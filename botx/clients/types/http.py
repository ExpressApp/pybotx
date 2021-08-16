"""Custom wrapper for HTTP request for BotX API."""
from enum import Enum
from io import BytesIO
from typing import Any, Dict, List, Optional, Tuple, Union

from pydantic import BaseModel, root_validator

PrimitiveDataType = Union[None, str, int, float, bool]


class ExpectedType(Enum):
    """Expected types of response body."""

    JSON = "JSON"  # noqa: WPS115
    BINARY = "BINARY"  # noqa: WPS115


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

    #: form data.
    data: Optional[Dict[str, Any]] = None  # noqa: WPS110

    #: file for httpx in {field_name: (file_name, file_content)}.
    files: Optional[Dict[str, Tuple[str, BytesIO]]] = None  # noqa: WPS234

    #: expected type of response body.
    expected_type: ExpectedType = ExpectedType.JSON

    # This field is used to provide handlers that are not in the range of 400 to 599.
    #: extra error codes.
    should_process_as_error: List[int] = []

    class Config:
        arbitrary_types_allowed = True


class HTTPResponse(BaseModel):
    """Wrapper for HTTP response."""

    #: response headers
    headers: Dict[str, str]

    #: response status code.
    status_code: int

    #: response body.
    json_body: Optional[Dict[str, Any]] = None

    #: response raw data.
    raw_data: Optional[bytes] = None

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

    @root_validator(pre=True)
    def check_fields(cls, values: Any) -> Any:  # noqa: N805, WPS110
        """Check if passed both `json_body` and `raw_data`."""
        json_body, raw_data = values.get("json_body"), values.get("raw_data")
        if (json_body is not None) and (raw_data is not None):
            raise ValueError("you cannot pass both `json_body` and `raw_data`.")

        return values
