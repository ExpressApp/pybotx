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

    #: `system:added_to_chat` event.
    added_to_chat = "system:added_to_chat"

    #: `system:deleted_from_chat` event.
    deleted_from_chat = "system:deleted_from_chat"

    #: `system:left_from_chat` event.
    left_from_chat = "system:left_from_chat"

    #: `system:internal_bot_notification` event
    internal_bot_notification = "system:internal_bot_notification"

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

    # botx
    botx = "botx"  # todo replies incoming with whith type


class UserKinds(str, Enum):
    """Enum for type of user."""

    #: normal user.
    user = "user"

    #: normal user, but will present if all users in chat are from the same CTS.
    cts_user = "cts_user"

    #: bot user.
    bot = "botx"


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

    #: forward entity.
    forward = "forward"

    #: reply entity.
    reply = "reply"


class AttachmentsTypes(str, Enum):
    """Types for attachments that could be received by bot."""

    image = "image"
    video = "video"
    document = "document"
    voice = "voice"
    contact = "contact"
    location = "location"
    link = "link"


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

    #: mention all users in chat
    all_members = "all"


class LinkProtos(str, Enum):
    """Enum for protos of links in attachments."""

    #: proto for attach with email.
    email = "mailto:"

    #: proto for attach with telephone number.
    telephone = "tel://"


class ClientPlatformEnum(str, Enum):
    """Enum for distinguishing client platforms."""

    #: Web platform.
    web = "web"

    #: Android platform.
    android = "android"

    #: iOS platform.
    ios = "ios"

    #: Desktop platform.
    desktop = "desktop"


class ButtonHandlerTypes(str, Enum):
    """Enum for markup's `handler` field."""

    #: bot side process.
    bot = "bot"

    #: client side process.
    client = "client"
