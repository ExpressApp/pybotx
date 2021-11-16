from botx.client.exceptions.base import BaseClientException


class CantUpdatePersonalChatError(BaseClientException):
    """Can't edit a personal chat."""


class InvalidUsersListError(BaseClientException):
    """Users list isn't correct."""


class ChatCreationProhibitedError(BaseClientException):
    """Bot doesn't have permissions to create chat."""


class ChatCreationError(BaseClientException):
    """Error while chat creation."""
