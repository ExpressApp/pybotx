"""Definition of enums that are used across different components of this library."""

from enum import Enum


class SystemEvents(Enum):
    """System enums that bot can retrieve from BotX API in message.

    !!! info
        NOTE: `file_transfer` is not a system event, but it is logical to place it in
        this enum.
    """

    chat_created = "system:chat_created"
    """`system:chat_created` event."""
    file_transfer = "file_transfer"
    """`file_transfer` message."""


class CommandTypes(str, Enum):
    """Enum that specify from whom command was received."""

    user = "user"
    """command received from user."""
    system = "system"
    """command received from system."""


class ChatTypes(str, Enum):
    """Enum for type of chat."""

    chat = "chat"
    """private chat for user with bot."""
    group_chat = "group_chat"
    """chat with several users."""
    channel = "channel"
    """channel chat."""


class UserKinds(str, Enum):
    """Enum for type of user."""

    user = "user"
    """normal user."""
    cts_user = "cts_user"
    """normal user, but will present if all users in chat are from the same CTS."""
    bot = "botx"
    """bot user."""


class Recipients(str, Enum):
    """Enum for default recipients value.

    - *all*: show message to all users in chat.
    """

    all: str = "all"


class Statuses(str, Enum):
    """Enum for status of operation in BotX API."""

    ok = "ok"
    """operation was successfully proceed."""
    error = "error"
    """there was an error while processing operation."""


class EntityTypes(str, Enum):
    """Types for entities that could be received by bot."""

    mention = "mention"
    """mention entity."""
