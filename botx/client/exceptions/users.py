from botx.client.exceptions.base import BaseClientException


class UserNotFoundError(BaseClientException):
    """User not found."""
