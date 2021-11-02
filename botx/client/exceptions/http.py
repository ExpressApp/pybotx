import httpx

from botx.client.exceptions.base import BaseClientException


class InvalidBotXResponseError(BaseClientException):
    """Received invalid response."""

    def __init__(self, response: httpx.Response) -> None:
        exc = BaseClientException.from_response(response)
        self.args = exc.args


class InvalidBotXStatusCodeError(InvalidBotXResponseError):
    """Received invalid status code."""


class InvalidBotXResponsePayloadError(InvalidBotXResponseError):
    """Received invalid status code."""
