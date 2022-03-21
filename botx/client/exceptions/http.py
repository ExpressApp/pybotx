import httpx

from botx.client.exceptions.base import BaseClientError


class InvalidBotXResponseError(BaseClientError):
    """Received invalid response."""

    def __init__(self, response: httpx.Response) -> None:
        exc = BaseClientError.from_response(response)
        self.args = exc.args


class InvalidBotXStatusCodeError(InvalidBotXResponseError):
    """Received invalid status code."""


class InvalidBotXResponsePayloadError(InvalidBotXResponseError):
    """Received invalid status code."""
