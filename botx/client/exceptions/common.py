from botx.client.exceptions.http import InvalidBotXStatusCodeError


class InvalidBotAccountError(InvalidBotXStatusCodeError):
    """Can't get token with given bot account."""


class RateLimitReachedError(InvalidBotXStatusCodeError):
    """Too many method requests."""


class PermissionDeniedError(InvalidBotXStatusCodeError):
    """Bot can't perform this action."""
