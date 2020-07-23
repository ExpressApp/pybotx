"""Exceptions that are used in this library."""
from typing import Any, Dict


class BotXException(Exception):
    """Base error for exception in this library."""

    #: template that should be rendered on __str__ call.
    message_template: str = ""

    def __init__(self, **kwargs: Any) -> None:
        """Init exception with passed query_params.

        Arguments:
            kwargs: key-arguments that will be stored in instance.
        """
        self.__dict__ = kwargs

    def __str__(self) -> str:
        """Render string representation.

        Returns:
            String representation of error.
        """
        return self.message_template.format(**self.__dict__)


class NoMatchFound(BotXException):
    """Raised by collector if no matching handler exists."""

    message_template = "handler for {search_param} not found"

    #: body for which handler was not found.
    search_param: str


class DependencyFailure(BotXException):
    """Raised when there is error in dependency and flow should be stopped."""


class BotXAPIError(BotXException):
    """Raised if there is an error in requests to BotX API."""

    message_template = "unable to send {method} {url} to BotX API ({status})"

    #: URL from request.
    url: str

    #: HTTP method.
    method: str

    #: response from API.
    response_content: Dict[str, Any]

    # HTTP status code.
    status: int


class ServerUnknownError(BotXException):
    """Raised if bot does not know host."""

    message_template = "unknown server {host}"

    #: host that is unregistered.
    host: str
