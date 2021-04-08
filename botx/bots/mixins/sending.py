"""Definition for mixin that defines helpers for sending message."""

from typing import Any, BinaryIO, Dict, Optional, TextIO, Union
from uuid import UUID

from botx.models.files import File
from botx.models.messages.message import Message
from botx.models.messages.sending.credentials import SendingCredentials
from botx.models.messages.sending.markup import MessageMarkup
from botx.models.messages.sending.message import SendingMessage
from botx.models.messages.sending.options import MessageOptions
from botx.models.messages.sending.payload import MessagePayload, UpdatePayload

try:
    from typing import Protocol  # noqa: WPS433
except ImportError:
    from typing_extensions import Protocol  # type: ignore  # noqa: WPS433, WPS440, F401


class ResultSendProtocol(Protocol):
    """Protocol for object that can create new or update message."""

    async def send_command_result(
        self,
        credentials: SendingCredentials,
        payload: MessagePayload,
    ) -> UUID:
        """Send command result."""

    async def send_direct_notification(
        self,
        credentials: SendingCredentials,
        payload: MessagePayload,
    ) -> UUID:
        """Send notification."""

    async def update_message(
        self,
        credentials: SendingCredentials,
        update: UpdatePayload,
    ) -> None:
        """Update existing message."""


class MessageSendProtocol(Protocol):
    """Protocol for object that can send complex message."""

    async def send(self, message: SendingMessage) -> UUID:
        """Send message."""


class SendingMixin:
    """Mixin that defines helpers for sending messages."""

    async def send_message(  # noqa: WPS211
        self: MessageSendProtocol,
        text: str,
        credentials: SendingCredentials,
        *,
        file: Optional[Union[BinaryIO, TextIO]] = None,
        markup: Optional[MessageMarkup] = None,
        options: Optional[MessageOptions] = None,
    ) -> UUID:
        """Send message as answer to command or notification to chat and get it id.

        Arguments:
            text: text that should be sent to client.
            credentials: credentials that are used for sending message.
            file: file that should be attached to message.
            markup: message markup that should be attached to message.
            options: extra options for message.

        Returns:
            `UUID` of sent event.
        """
        message = SendingMessage(
            text=text,
            markup=markup,
            options=options,
            credentials=credentials,
        )
        if file:
            message.add_file(file)

        return await self.send(message)

    async def send(
        self: ResultSendProtocol,
        message: SendingMessage,
        *,
        update: bool = False,
    ) -> UUID:
        """Send message as direct notification to chat and get it id.

        Arguments:
            message: message that should be sent to chat.
            update: if True then check, that `message_id` was set in credentials and
                update existing message with this ID.

        Returns:
            `UUID` of sent event.
        """
        if message.credentials.message_id is not None and update:
            await self.update_message(
                message.credentials.copy(
                    update={"sync_id": message.credentials.message_id},
                ),
                UpdatePayload.from_sending_payload(message.payload),
            )
            return message.credentials.message_id

        return await self.send_direct_notification(message.credentials, message.payload)

    async def answer_message(  # noqa: WPS211
        self: MessageSendProtocol,
        text: str,
        message: Message,
        *,
        metadata: Optional[Dict[str, Any]] = None,
        file: Optional[Union[BinaryIO, TextIO, File]] = None,
        markup: Optional[MessageMarkup] = None,
        options: Optional[MessageOptions] = None,
    ) -> UUID:
        """Answer on incoming message and return id of new message..

        !!! warning
            This method should be used only in handlers.

        Arguments:
            text: text that should be sent in message.
            message: incoming message.
            file: file that can be attached to the message.
            markup: bubbles and keyboard that can be attached to the message.
            options: additional message options, like mentions or notifications
                configuration.
            metadata: dict of message metadata

        Returns:
            `UUID` of sent event.
        """
        sending_message = SendingMessage(
            text=text,
            credentials=message.credentials,
            markup=markup,
            options=options,
            metadata=metadata,
        )
        if file:
            sending_message.add_file(file)

        return await self.send(sending_message)

    async def send_file(
        self: MessageSendProtocol,
        file: Union[TextIO, BinaryIO, File],
        credentials: SendingCredentials,
        filename: Optional[str] = None,
    ) -> UUID:
        """Send file in chat and return id of message.

        Arguments:
            file: file-like object that will be sent to chat.
            credentials: credentials of chat where file should be sent.
            filename: name for file that will be used if it can not be accessed from
                `file` argument.

        Returns:
            `UUID` of sent event.
        """
        message = SendingMessage(credentials=credentials)
        message.add_file(file, filename)
        return await self.send(message)
