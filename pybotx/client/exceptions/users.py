from pybotx.client.exceptions.base import BaseClientError


class UserNotFoundError(BaseClientError):
    """User not found."""
