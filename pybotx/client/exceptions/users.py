from pybotx.client.exceptions.base import BaseClientError


class UserNotFoundError(BaseClientError):
    """User not found."""


class InvalidProfileDataError(BaseClientError):
    """Invalid profile data."""


class NoUserKindSelectedError(BaseClientError):
    """No user kind selected."""
