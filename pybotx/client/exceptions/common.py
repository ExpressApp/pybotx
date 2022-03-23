from pybotx.client.exceptions.base import BaseClientError


class InvalidBotAccountError(BaseClientError):
    """Can't get token with given bot account."""


class RateLimitReachedError(BaseClientError):
    """Too many method requests."""


class PermissionDeniedError(BaseClientError):
    """Bot can't perform this action."""


class ChatNotFoundError(BaseClientError):
    """Chat with specified group_chat_id not found."""
