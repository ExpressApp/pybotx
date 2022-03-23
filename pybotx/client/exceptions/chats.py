from pybotx.client.exceptions.base import BaseClientError


class CantUpdatePersonalChatError(BaseClientError):
    """Can't edit a personal chat."""


class InvalidUsersListError(BaseClientError):
    """Users list isn't correct."""


class ChatCreationProhibitedError(BaseClientError):
    """Bot doesn't have permissions to create chat."""


class ChatCreationError(BaseClientError):
    """Error while chat creation."""
