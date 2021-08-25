import pytest
from pydantic import ValidationError

from botx.clients.types.http import HTTPResponse


def test_response_validation():
    with pytest.raises(ValidationError):
        HTTPResponse(
            headers={},
            status_code=200,
            json_body={"status": "ok"},
            raw_data=b"content",
        )
