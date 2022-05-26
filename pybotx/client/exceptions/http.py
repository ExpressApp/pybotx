from typing import Any

import httpx

from pybotx.client.exceptions.base import BaseClientError


class InvalidBotXResponseError(BaseClientError):
    """Received invalid response."""

    def __init__(self, response: httpx.Response) -> None:
        exc = BaseClientError.from_response(response)
        self.response = response

        self.args = exc.args

    def __reduce__(self) -> Any:
        # This method required to pass exception from pybotx logger to bot logger.
        return type(self), (self.response,)  # pragma: no cover


class InvalidBotXStatusCodeError(InvalidBotXResponseError):
    """Received invalid status code."""


class InvalidBotXResponsePayloadError(InvalidBotXResponseError):
    """Received invalid status code."""
