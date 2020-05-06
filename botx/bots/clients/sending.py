"""Definition for mixin that defines helpers for sending message."""
from typing import Awaitable, BinaryIO, Callable, Optional, TextIO, Union
from uuid import UUID

from botx import clients
from botx.models import files, messages, sending


class SendingMixin:
    client: clients.AsyncClient
    _obtain_token: Callable[[sending.SendingCredentials], Awaitable[None]]

    async def send_message(
        self,
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
        await self._obtain_token(credentials)

        payload = sending.MessagePayload(
            text=text,
            file=files.File.from_file(file) if file else None,
            markup=markup or sending.MessageMarkup(),
            options=options or sending.MessageOptions(),
        )

        if credentials.sync_id:
            return await self.client.send_command_result(credentials, payload)

        return await self.client.send_notification(credentials, payload)

    async def send(self, message: messages.SendingMessage) -> UUID:
        """Send message as answer to command or notification to chat and get it id.

        Arguments:
            message: message that should be sent to chat.

        Returns:
            `UUID` of sent event.
        """
        await self._obtain_token(message.credentials)

        if message.sync_id:
            return await self.client.send_command_result(
                message.credentials, message.payload
            )

        return await self.client.send_notification(message.credentials, message.payload)

    async def answer_message(
        self,
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
