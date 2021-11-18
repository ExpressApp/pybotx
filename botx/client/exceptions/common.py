from botx.client.exceptions.base import BaseClientException


class InvalidBotAccountError(BaseClientException):
    """Can't get token with given bot account."""


class RateLimitReachedError(BaseClientException):
    """Too many method requests."""


class PermissionDeniedError(BaseClientException):
    """Bot can't perform this action."""


class ChatNotFoundError(BaseClientException):
    """Chat with specified chat_id not found."""
