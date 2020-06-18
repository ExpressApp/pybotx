"""Definition of message object that is used in all bot handlers."""
from __future__ import annotations

from functools import partial
from typing import Any, List, Optional, Type
from uuid import UUID

from botx.bots import bots
from botx.models.datastructures import State
from botx.models.files import File
from botx.models.messages.incoming_message import (
    Command,
    Entity,
    IncomingMessage,
    Sender,
)
from botx.models.messages.sending.credentials import SendingCredentials


class _ProxyProperty:
    def __init__(self, proxy_attribute_name: str, *nested_fields: str) -> None:
        self.proxy_attribute_name = proxy_attribute_name
        self.nested_fields = list(nested_fields)

    def __get__(self, instance: Message, _owner: Type[Message]) -> Any:
        proxy_object = getattr(instance, self.proxy_attribute_name)
        accessed_result = proxy_object
        for nested_field in self.nested_fields:
            accessed_result = getattr(accessed_result, nested_field)
        return accessed_result

    def __set_name__(self, _owner: Type[Message], name: str) -> None:
        self.nested_fields.append(name)


def _proxy_property(proxy_attribute_name: str, *nested_fields: str) -> Any:
    return _ProxyProperty(proxy_attribute_name, *nested_fields)


_message_proxy_property = partial(_proxy_property, "incoming_message")
_user_proxy_property = partial(_message_proxy_property, "user")


class Message:
    """Message that is used in handlers."""

    #: incoming message from BotX.
    incoming_message: IncomingMessage

    #: bot that handles this message processing.
    bot: "bots.Bot"

    #: state of message during processing.
    state: State

    #: ID of message event.
    sync_id: UUID = _message_proxy_property()
    #: ID of bot that handles message in Express.
    bot_id: UUID = _message_proxy_property()

    #: access to command information.
    command: Command = _message_proxy_property()
    #: command body.
    body: str = _message_proxy_property("command")
    #: command data.
    data: dict = _message_proxy_property("command")  # noqa: WPS110
    #: command metadata.
    metadata: dict = _message_proxy_property("command")

    #: file from message.
    file: Optional[File] = _message_proxy_property()

    #: information about user that sent message.
    user: Sender = _message_proxy_property()
    #: HUID of user.
    user_huid: Optional[UUID] = _user_proxy_property()
    #: AD login of user.
    ad_login: Optional[str] = _user_proxy_property()
    #: AD domain of user.
    ad_domain: Optional[str] = _user_proxy_property()
    #: ID of chat from which message was received.
    group_chat_id: UUID = _user_proxy_property()
    #: type of chat.
    chat_type: str = _user_proxy_property()
    #: host of CTS from which message was received.
    host: str = _user_proxy_property()

    #: external entities in message (mentions, forwards, etc)
    entities: List[Entity] = _message_proxy_property()

    #: credentials from message for using in requests.
    credentials: SendingCredentials

    #: flag for marking that message was received from button.
    sent_from_button: bool

    def __init__(self, message: IncomingMessage, bot: "bots.Bot") -> None:
        """Initialize and update fields.

        Arguments:
            message: incoming message.
            bot: bot that handles message processing.
        """
        self.incoming_message = message
        self.bot = bot

        self.state = State()

        self.credentials = SendingCredentials(
            sync_id=self.sync_id,
            bot_id=self.bot_id,
            host=self.host,
            chat_id=self.group_chat_id,
        )

        self.sent_from_button = (
            self.data.get("ui", False) if isinstance(self.command.data, dict) else False
        )

    @classmethod
    def from_dict(cls, message: dict, bot: "bots.Bot") -> Message:
        """Parse incoming dict into message.

        Arguments:
            message: incoming message to bot as dictionary.
            bot: bot that handles message.

        Returns:
            Parsed message.
        """
        return cls(IncomingMessage(**message), bot)
