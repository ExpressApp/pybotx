from botx.client.exceptions.http import InvalidBotXStatusCodeError


class ChatCreationProhibitedError(InvalidBotXStatusCodeError):
    """Bot doesn't have permissions to create chat."""


class ChatCreationError(InvalidBotXStatusCodeError):
    """Error while chat creation."""
