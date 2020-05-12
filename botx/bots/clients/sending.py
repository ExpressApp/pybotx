"""Definition for mixin that defines helpers for sending message."""
from typing import TYPE_CHECKING, BinaryIO, Optional, TextIO, Union
from uuid import UUID

from botx.models import files, messages, sending

if TYPE_CHECKING:
    from botx.bots.bots import Bot  # noqa: WPS433


class SendingMixin:
    """Mixin that defines helpers for sending messages."""

    async def send_message(  # type: ignore
        self: "Bot",
        text: str,
        credentials: sending.SendingCredentials,
        *,
        file: Optional[Union[BinaryIO, TextIO]] = None,
        markup: Optional[sending.MessageMarkup] = None,
        options: Optional[sending.MessageOptions] = None,
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
        message = messages.SendingMessage(
            text=text, markup=markup, options=options, credentials=credentials,
        )
        if file:
            message.add_file(file)

        return await self.send(message)

    async def send(  # type: ignore
        self: "Bot", message: messages.SendingMessage
    ) -> UUID:
        """Send message as answer to command or notification to chat and get it id.

        Arguments:
            message: message that should be sent to chat.

        Returns:
            `UUID` of sent event.
        """
        if message.sync_id:
            return await self.send_command_result(message.credentials, message.payload)

        return await self.send_direct_notification(message.credentials, message.payload)

    async def answer_message(  # type: ignore
        self: "Bot",
        text: str,
        message: messages.Message,
        *,
        file: Optional[Union[BinaryIO, TextIO, files.File]] = None,
        markup: Optional[sending.MessageMarkup] = None,
        options: Optional[sending.MessageOptions] = None,
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

        Returns:
            `UUID` of sent event.
        """
        sending_message = messages.SendingMessage(
            text=text, credentials=message.credentials, markup=markup, options=options
        )
        if file:
            sending_message.add_file(file)

        return await self.send(sending_message)

    async def send_file(
        self,
        file: Union[TextIO, BinaryIO, files.File],
        credentials: sending.SendingCredentials,
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
        message = messages.SendingMessage(credentials=credentials)
        message.add_file(file, filename)
        return await self.send(message)
