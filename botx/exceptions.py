"""Exceptions that are used in this library."""
from typing import Any

# All inits here are required for auto docs


class NoMatchFound(Exception):
    """Raised by collector if no matching handler exists."""

    def __init__(self, *args: Any) -> None:
        """Init NoMatchFound exception."""
        super().__init__(*args)


class DependencyFailure(Exception):
    """Raised when there is error in dependency and flow should be stopped."""

    def __init__(self, *args: Any) -> None:
        """Init DependencyFailure exception."""
        super().__init__(*args)


class BotXAPIError(Exception):
    """Raised if there is an error in requests to BotX API."""

    def __init__(self, *args: Any) -> None:
        """Init BotXAPIError exception."""
        super().__init__(*args)


class ServerUnknownError(Exception):
    """Raised if bot does not know host."""

    def __init__(self, *args: Any) -> None:
        """Init ServerUnknownError exception."""
        super().__init__(*args)
