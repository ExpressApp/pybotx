from __future__ import annotations

import asyncio
from typing import Any
from uuid import UUID

from pybotx.domain.contextvars import bot_id_var, chat_id_var
from pybotx.domain.converters import resolve_message_options
from pybotx.domain.errors import AnswerDestinationLookupError
from pybotx.domain.missing import Missing, Undefined
from pybotx.domain.models.attachments import IncomingFileAttachment, OutgoingAttachment
from pybotx.domain.models.message.bulk_results import BulkSendItemResult, BulkSendResult
from pybotx.domain.models.message.markup import BubbleMarkup, KeyboardMarkup
from pybotx.domain.models.message.message_options import MessageOptions
from pybotx.domain.models.message.outgoing_message import OutgoingMessage


class BotNotificationsMixin:
    async def answer_message(
        self,
        body: str,
        *,
        metadata: Missing[dict[str, Any]] = Undefined,
        bubbles: Missing[BubbleMarkup] = Undefined,
        keyboard: Missing[KeyboardMarkup] = Undefined,
        file: Missing[IncomingFileAttachment | OutgoingAttachment] = Undefined,
        recipients: Missing[list[UUID]] = Undefined,
        silent_response: Missing[bool] = Undefined,
        markup_auto_adjust: Missing[bool] = Undefined,
        stealth_mode: Missing[bool] = Undefined,
        send_push: Missing[bool] = Undefined,
        ignore_mute: Missing[bool] = Undefined,
        options: MessageOptions | None = None,
        wait_callback: bool = True,
        callback_timeout: float | None = None,
    ) -> UUID:
        """Answer to incoming message.

        Works just like `Bot.send`, but `bot_id` and `chat_id` are
        taken from the incoming message.

        :param body: Message body.
        :param metadata: Notification options.
        :param bubbles: Bubbles (buttons attached to message) markup.
        :param keyboard: Keyboard (buttons below message input) markup.
        :param file: Attachment.
        :param recipients: List of recipients, empty for all in chat.
        :param silent_response: (BotX default: False) Exclude next user
            messages from history.
        :param markup_auto_adjust: (BotX default: False) Move button to next
            row, if its text doesn't fit.
        :param stealth_mode: (BotX default: False) Enable stealth mode.
        :param send_push: (BotX default: True) Send push notification on
            devices.
        :param ignore_mute: (BotX default: False) Ignore mute or dnd (do not
            disturb).
        :param wait_callback: Block method call until callback received.
        :param callback_timeout: Callback timeout in seconds (or `None` for
            endless waiting).

        :raises AnswerDestinationLookupError: If you try to answer without
            receiving incoming message.

        :return: Notification sync_id.
        """

        try:
            bot_id = bot_id_var.get()
            chat_id = chat_id_var.get()
        except LookupError as exc:
            raise AnswerDestinationLookupError from exc

        return await self.send_message(
            bot_id=bot_id,
            chat_id=chat_id,
            body=body,
            metadata=metadata,
            bubbles=bubbles,
            keyboard=keyboard,
            file=file,
            recipients=recipients,
            silent_response=silent_response,
            markup_auto_adjust=markup_auto_adjust,
            stealth_mode=stealth_mode,
            send_push=send_push,
            ignore_mute=ignore_mute,
            options=options,
            wait_callback=wait_callback,
            callback_timeout=callback_timeout,
        )

    async def send(
        self,
        *,
        message: OutgoingMessage,
        wait_callback: bool = True,
        callback_timeout: float | None = None,
    ) -> UUID:
        """Send internal notification.

        :param message: Built outgoing message.
        :param wait_callback: Wait for callback.
        :param callback_timeout: Timeout for waiting for callback.

        :return: Notification sync_id.
        """

        return await self.send_message(
            bot_id=message.bot_id,
            chat_id=message.chat_id,
            body=message.body,
            metadata=message.metadata,
            bubbles=message.bubbles,
            keyboard=message.keyboard,
            file=message.file,
            recipients=message.recipients,
            silent_response=message.silent_response,
            markup_auto_adjust=message.markup_auto_adjust,
            stealth_mode=message.stealth_mode,
            send_push=message.send_push,
            ignore_mute=message.ignore_mute,
            wait_callback=wait_callback,
            callback_timeout=callback_timeout,
        )

    async def bulk_send(
        self,
        *,
        messages: list[OutgoingMessage] | tuple[OutgoingMessage, ...],
        options: MessageOptions | None = None,
        max_concurrency: int | None = None,
        wait_callback: bool = True,
        callback_timeout: float | None = None,
    ) -> BulkSendResult:
        message_list = list(messages)
        if not message_list:
            return BulkSendResult(items=[])

        if options is not None:
            resolved_messages: list[OutgoingMessage] = []
            for message in message_list:
                (
                    recipients,
                    silent_response,
                    markup_auto_adjust,
                    stealth_mode,
                    send_push,
                    ignore_mute,
                ) = resolve_message_options(
                    options,
                    recipients=message.recipients,
                    silent_response=message.silent_response,
                    markup_auto_adjust=message.markup_auto_adjust,
                    stealth_mode=message.stealth_mode,
                    send_push=message.send_push,
                    ignore_mute=message.ignore_mute,
                )
                resolved_messages.append(
                    OutgoingMessage(
                        bot_id=message.bot_id,
                        chat_id=message.chat_id,
                        body=message.body,
                        metadata=message.metadata,
                        bubbles=message.bubbles,
                        keyboard=message.keyboard,
                        file=message.file,
                        recipients=recipients,
                        silent_response=silent_response,
                        markup_auto_adjust=markup_auto_adjust,
                        stealth_mode=stealth_mode,
                        send_push=send_push,
                        ignore_mute=ignore_mute,
                    ),
                )
            message_list = resolved_messages

        if max_concurrency is None or max_concurrency <= 1:
            items: list[BulkSendItemResult] = []
            for message in message_list:
                try:
                    sync_id = await self.send(
                        message=message,
                        wait_callback=wait_callback,
                        callback_timeout=callback_timeout,
                    )
                except Exception as exc:
                    items.append(BulkSendItemResult(message=message, error=exc))
                else:
                    items.append(BulkSendItemResult(message=message, sync_id=sync_id))
            return BulkSendResult(items=items)

        semaphore = asyncio.Semaphore(max_concurrency)

        async def _run(message: OutgoingMessage) -> BulkSendItemResult:
            async with semaphore:
                try:
                    sync_id = await self.send(
                        message=message,
                        wait_callback=wait_callback,
                        callback_timeout=callback_timeout,
                    )
                except Exception as exc:
                    return BulkSendItemResult(message=message, error=exc)
                return BulkSendItemResult(message=message, sync_id=sync_id)

        results = await asyncio.gather(*(_run(message) for message in message_list))
        return BulkSendResult(items=list(results))

    async def send_message(
        self,
        *,
        bot_id: UUID,
        chat_id: UUID,
        body: str,
        metadata: Missing[dict[str, Any]] = Undefined,
        bubbles: Missing[BubbleMarkup] = Undefined,
        keyboard: Missing[KeyboardMarkup] = Undefined,
        file: Missing[IncomingFileAttachment | OutgoingAttachment] = Undefined,
        silent_response: Missing[bool] = Undefined,
        markup_auto_adjust: Missing[bool] = Undefined,
        recipients: Missing[list[UUID]] = Undefined,
        stealth_mode: Missing[bool] = Undefined,
        send_push: Missing[bool] = Undefined,
        ignore_mute: Missing[bool] = Undefined,
        options: MessageOptions | None = None,
        wait_callback: bool = True,
        callback_timeout: float | None = None,
    ) -> UUID:
        """Send message to chat.

        :param bot_id: Bot which should perform the request.
        :param chat_id: Target chat id.
        :param body: Message body.
        :param metadata: Notification options.
        :param bubbles: Bubbles (buttons attached to message) markup.
        :param keyboard: Keyboard (buttons below message input) markup.
        :param file: Attachment.
        :param recipients: List of recipients, empty for all in chat.
        :param silent_response: (BotX default: False) Exclude next user
            messages from history.
        :param markup_auto_adjust: (BotX default: False) Move button to next
            row, if its text doesn't fit.
        :param stealth_mode: (BotX default: False) Enable stealth mode.
        :param send_push: (BotX default: True) Send push notification on
            devices.
        :param ignore_mute: (BotX default: False) Ignore mute or dnd (do not
            disturb).
        :param wait_callback: Block method call until callback received.
        :param callback_timeout: Callback timeout in seconds (or `None` for
            endless waiting).

        :return: Notification sync_id.
        """
        (
            recipients,
            silent_response,
            markup_auto_adjust,
            stealth_mode,
            send_push,
            ignore_mute,
        ) = resolve_message_options(
            options,
            recipients=recipients,
            silent_response=silent_response,
            markup_auto_adjust=markup_auto_adjust,
            stealth_mode=stealth_mode,
            send_push=send_push,
            ignore_mute=ignore_mute,
        )

        return await self._botx_api.send_message(
            bot_id=bot_id,
            chat_id=chat_id,
            body=body,
            metadata=metadata,
            bubbles=bubbles,
            keyboard=keyboard,
            file=file,
            silent_response=silent_response,
            markup_auto_adjust=markup_auto_adjust,
            recipients=recipients,
            stealth_mode=stealth_mode,
            send_push=send_push,
            ignore_mute=ignore_mute,
            wait_callback=wait_callback,
            callback_timeout=callback_timeout,
        )

    async def send_message_sync(
        self,
        *,
        bot_id: UUID,
        chat_id: UUID,
        body: str,
        metadata: Missing[dict[str, Any]] = Undefined,
        bubbles: Missing[BubbleMarkup] = Undefined,
        keyboard: Missing[KeyboardMarkup] = Undefined,
        file: Missing[IncomingFileAttachment | OutgoingAttachment] = Undefined,
        silent_response: Missing[bool] = Undefined,
        markup_auto_adjust: Missing[bool] = Undefined,
        recipients: Missing[list[UUID]] = Undefined,
        stealth_mode: Missing[bool] = Undefined,
        send_push: Missing[bool] = Undefined,
        ignore_mute: Missing[bool] = Undefined,
        options: MessageOptions | None = None,
    ) -> UUID:
        """Send message to chat synchronously (BotX >= 3.58).

        :param bot_id: Bot which should perform the request.
        :param chat_id: Target chat id.
        :param body: Message body.
        :param metadata: Notification options.
        :param bubbles: Bubbles (buttons attached to message) markup.
        :param keyboard: Keyboard (buttons below message input) markup.
        :param file: Attachment.
        :param recipients: List of recipients, empty for all in chat.
        :param silent_response: (BotX default: False) Exclude next user
            messages from history.
        :param markup_auto_adjust: (BotX default: False) Move button to next
            row, if its text doesn't fit.
        :param stealth_mode: (BotX default: False) Enable stealth mode.
        :param send_push: (BotX default: True) Send push notification on
            devices.
        :param ignore_mute: (BotX default: False) Ignore mute or dnd (do not
            disturb).

        :return: Notification sync_id.
        """
        (
            recipients,
            silent_response,
            markup_auto_adjust,
            stealth_mode,
            send_push,
            ignore_mute,
        ) = resolve_message_options(
            options,
            recipients=recipients,
            silent_response=silent_response,
            markup_auto_adjust=markup_auto_adjust,
            stealth_mode=stealth_mode,
            send_push=send_push,
            ignore_mute=ignore_mute,
        )

        return await self._botx_api.send_message_sync(
            bot_id=bot_id,
            chat_id=chat_id,
            body=body,
            metadata=metadata,
            bubbles=bubbles,
            keyboard=keyboard,
            file=file,
            silent_response=silent_response,
            markup_auto_adjust=markup_auto_adjust,
            recipients=recipients,
            stealth_mode=stealth_mode,
            send_push=send_push,
            ignore_mute=ignore_mute,
        )

    async def send_internal_bot_notification(
        self,
        *,
        bot_id: UUID,
        chat_id: UUID,
        data: dict[str, Any],
        opts: Missing[dict[str, Any]] = Undefined,
        recipients: Missing[list[UUID]] = Undefined,
        wait_callback: bool = True,
        callback_timeout: float | None = None,
    ) -> UUID:
        """Send internal notification.

        :param bot_id: Bot which should perform the request.
        :param chat_id: Target chat id.
        :param data: Notification payload.
        :param opts: Notification options.
        :param recipients: List of bot uuids, empty for all in chat.
        :param wait_callback: Wait for callback.
        :param callback_timeout: Timeout for waiting for callback.

        :return: Notification sync_id.
        """
        return await self._botx_api.send_internal_bot_notification(
            bot_id=bot_id,
            chat_id=chat_id,
            data=data,
            opts=opts,
            recipients=recipients,
            wait_callback=wait_callback,
            callback_timeout=callback_timeout,
        )
