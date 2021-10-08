from botx.client.exceptions.http import BaseBotXAPIError


class ChatCreationProhibitedError(BaseBotXAPIError):
    """Bot doesn't have permissions to create chat."""


class ChatCreationError(BaseBotXAPIError):
    """Error while chat creation."""
