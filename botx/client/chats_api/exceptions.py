from botx.client.exceptions.base import BaseClientException


class ChatMembersNotModifiableError(BaseClientException):
    """Can't edit a list of personal chat administrators."""


class AdministratorsNotChangedError(BaseClientException):
    """Can't change administrators."""


class ChatCreationProhibitedError(BaseClientException):
    """Bot doesn't have permissions to create chat."""


class ChatCreationError(BaseClientException):
    """Error while chat creation."""
