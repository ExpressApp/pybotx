from pybotx.client.exceptions.base import BaseClientError


class CantUpdatePersonalChatError(BaseClientError):
    """Can't edit a personal chat."""


class InvalidUsersListError(BaseClientError):
    """Users list isn't correct."""


class ChatCreationProhibitedError(BaseClientError):
    """Bot doesn't have permissions to create chat."""


class ChatCreationError(BaseClientError):
    """Error while chat creation."""


class ThreadAlreadyExistsError(BaseClientError):
    """Thread is already exists."""


class ThreadCreationError(BaseClientError):
    """Creating a thread for a deleted message."""


class ThreadCreationProhibitedError(BaseClientError):
    """
    Error while permission checks.

    1. Bot has no permissions to create thread
    2. Threads are not allowed for this chat
    3. Bot is not a chat member where message is located
    4. Message is located in personal chat
    5. Usupported event type
    6. Unsuppoerted chat type
    7. No access for message
    8. Message in stealth mode
    """
