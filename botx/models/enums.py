"""Definition of enums that are used across different components of this library."""

from enum import Enum


class SystemEvents(Enum):
    """System enums that bot can retrieve from BotX API in message.

    !!! info
        NOTE: `file_transfer` is not a system event, but it is logical to place it in
        this enum.
    """

    #: `system:chat_created` event.
    chat_created = "system:chat_created"

    #: `file_transfer` message.
    file_transfer = "file_transfer"


class CommandTypes(str, Enum):
    """Enum that specify from whom command was received."""

    #: command received from user.
    user = "user"

    #: command received from system.
    system = "system"


class ChatTypes(str, Enum):
    """Enum for type of chat."""

    #: private chat for user with bot.
    chat = "chat"

    #: chat with several users.
    group_chat = "group_chat"

    #: channel chat.
    channel = "channel"


class UserKinds(str, Enum):
    """Enum for type of user."""

    #: normal user.
    user = "user"

    #: normal user, but will present if all users in chat are from the same CTS.
    cts_user = "cts_user"

    #: bot user.
    bot = "botx"


class Recipients(str, Enum):
    """Enum for default recipients value."""

    #: show message to all users in chat.
    all: str = "all"


class Statuses(str, Enum):
    """Enum for status of operation in BotX API."""

    #: operation was successfully proceed.
    ok = "ok"

    #: there was an error while processing operation.
    error = "error"


class EntityTypes(str, Enum):
    """Types for entities that could be received by bot."""

    #: mention entity.
    mention = "mention"


class MentionTypes(str, Enum):
    """Enum for available validated_values in mentions."""

    #: mention single user from chat in message.
    user = "user"

    #: mention user by user_huid.
    contact = "contact"

    #: mention chat in message.
    chat = "chat"

    #: mention channel in message.
    channel = "channel"
