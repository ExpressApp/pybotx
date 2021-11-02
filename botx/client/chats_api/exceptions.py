from botx.client.exceptions.base import BaseClientException


class ChatCreationProhibitedError(BaseClientException):
    """Bot doesn't have permissions to create chat."""


class ChatCreationError(BaseClientException):
    """Error while chat creation."""
