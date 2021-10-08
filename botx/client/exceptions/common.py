from botx.client.exceptions.http import BaseBotXAPIError


class InvalidBotAccountError(BaseBotXAPIError):
    """Can't get token with given bot account."""


class RateLimitReachedError(BaseBotXAPIError):
    """Too many method requests."""
