"""Exceptions that are used in this library."""
from typing import Any, Dict

# All inits here are required for auto docs


class BotXException(Exception):
    """Base error for exception in this library."""

    message_template: str = ""
    """template that should be rendered on __str__ call."""

    def __init__(self, **kwargs: Any) -> None:
        """Init exception with passed params.

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
    search_param: str


class DependencyFailure(BotXException):
    """Raised when there is error in dependency and flow should be stopped."""


class BotXAPIError(BotXException):
    """Raised if there is an error in requests to BotX API."""

    message_template = "unable to send {method.upper()} {url} to BotX API ({status})"
    url: str
    method: str
    response_content: Dict[str, Any]
    status: int


class ServerUnknownError(BotXException):
    """Raised if bot does not know host."""

    message_template = "unknown server {host}"
    host: str
