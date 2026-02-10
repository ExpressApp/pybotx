from __future__ import annotations

import asyncio
from typing import Any, TypeAlias
from uuid import UUID

from pybotx.domain.converters import resolve_message_options
from pybotx.domain.missing import Missing, MissingOptional, Undefined
from pybotx.domain.models.attachments import IncomingFileAttachment, OutgoingAttachment
from pybotx.domain.models.message.bulk_results import (
    BulkEditItemResult,
    BulkEditResult,
    BulkReplyItemResult,
    BulkReplyResult,
)
from pybotx.domain.models.message.edit_message import EditMessage
from pybotx.domain.models.message.incoming_message import IncomingMessage
from pybotx.domain.models.message.markup import BubbleMarkup, KeyboardMarkup
from pybotx.domain.models.message.message_options import MessageOptions
from pybotx.domain.models.message.message_status import MessageStatus
from pybotx.domain.models.message.reply_message import ReplyMessage

MissingOptionalAttachment: TypeAlias = MissingOptional[
    IncomingFileAttachment | OutgoingAttachment
]


class BotEventsMixin:
    async def edit(
        self,
        *,
        message: EditMessage,
    ) -> None:
        """Edit message.

        :param message: Built outgoing edit message.
        """

        await self.edit_message(
            bot_id=message.bot_id,
            sync_id=message.sync_id,
            body=message.body,
            metadata=message.metadata,
            bubbles=message.bubbles,
            keyboard=message.keyboard,
            file=message.file,
            markup_auto_adjust=message.markup_auto_adjust,
        )

    async def bulk_edit(
        self,
        *,
        messages: list[EditMessage] | tuple[EditMessage, ...],
        max_concurrency: int | None = None,
    ) -> BulkEditResult:
        message_list = list(messages)
        if not message_list:
            return BulkEditResult(items=[])

        if max_concurrency is None or max_concurrency <= 1:
            items: list[BulkEditItemResult] = []
            for message in message_list:
                try:
                    await self.edit(message=message)
                except Exception as exc:
                    items.append(BulkEditItemResult(message=message, error=exc))
                else:
                    items.append(BulkEditItemResult(message=message))
            return BulkEditResult(items=items)

        semaphore = asyncio.Semaphore(max_concurrency)

        async def _run(message: EditMessage) -> BulkEditItemResult:
            async with semaphore:
                try:
                    await self.edit(message=message)
                except Exception as exc:
                    return BulkEditItemResult(message=message, error=exc)
                return BulkEditItemResult(message=message)

        results = await asyncio.gather(*(_run(message) for message in message_list))
        return BulkEditResult(items=list(results))

    async def edit_message(
        self,
        *,
        bot_id: UUID,
        sync_id: UUID,
        body: Missing[str] = Undefined,
        metadata: Missing[dict[str, Any]] = Undefined,
        bubbles: Missing[BubbleMarkup] = Undefined,
        keyboard: Missing[KeyboardMarkup] = Undefined,
        file: MissingOptionalAttachment = Undefined,
        markup_auto_adjust: Missing[bool] = Undefined,
        options: MessageOptions | None = None,
    ) -> None:
        """Edit message.

        :param bot_id: Bot which should perform the request.
        :param sync_id: `sync_id` of message to update.
        :param body: New message body. Skip to leave previous body or pass
            empty string to clean it.
        :param metadata: Notification options. Skip to leave previous metadata.
        :param bubbles: Bubbles (buttons attached to message) markup. Skip to
            leave previous bubbles.
        :param keyboard: Keyboard (buttons below message input) markup. Skip
            to leave previous keyboard.
        :param file: Attachment. Skip to leave previous file or pass `None`
            to clean it.
        :param markup_auto_adjust: (BotX default: False) Move button to next
            row, if its text doesn't fit.
        """
        (
            _recipients,
            _silent_response,
            markup_auto_adjust,
            _stealth_mode,
            _send_push,
            _ignore_mute,
        ) = resolve_message_options(
            options,
            markup_auto_adjust=markup_auto_adjust,
        )

        await self._botx_api.edit_message(
            bot_id=bot_id,
            sync_id=sync_id,
            body=body,
            metadata=metadata,
            bubbles=bubbles,
            keyboard=keyboard,
            file=file,
            markup_auto_adjust=markup_auto_adjust,
        )

    async def reply(
        self,
        *,
        message: ReplyMessage,
    ) -> None:
        """Reply message.

        :param message: Built outgoing reply message.
        """

        await self.reply_message(
            bot_id=message.bot_id,
            sync_id=message.sync_id,
            body=message.body,
            metadata=message.metadata,
            bubbles=message.bubbles,
            keyboard=message.keyboard,
            file=message.file,
            silent_response=message.silent_response,
            markup_auto_adjust=message.markup_auto_adjust,
            stealth_mode=message.stealth_mode,
            send_push=message.send_push,
            ignore_mute=message.ignore_mute,
        )

    async def bulk_reply(
        self,
        *,
        messages: list[ReplyMessage] | tuple[ReplyMessage, ...],
        options: MessageOptions | None = None,
        max_concurrency: int | None = None,
    ) -> BulkReplyResult:
        message_list = list(messages)
        if not message_list:
            return BulkReplyResult(items=[])

        if options is not None:
            resolved_messages: list[ReplyMessage] = []
            for message in message_list:
                (
                    _recipients,
                    silent_response,
                    markup_auto_adjust,
                    stealth_mode,
                    send_push,
                    ignore_mute,
                ) = resolve_message_options(
                    options,
                    silent_response=message.silent_response,
                    markup_auto_adjust=message.markup_auto_adjust,
                    stealth_mode=message.stealth_mode,
                    send_push=message.send_push,
                    ignore_mute=message.ignore_mute,
                )
                resolved_messages.append(
                    ReplyMessage(
                        bot_id=message.bot_id,
                        sync_id=message.sync_id,
                        body=message.body,
                        metadata=message.metadata,
                        bubbles=message.bubbles,
                        keyboard=message.keyboard,
                        file=message.file,
                        silent_response=silent_response,
                        markup_auto_adjust=markup_auto_adjust,
                        stealth_mode=stealth_mode,
                        send_push=send_push,
                        ignore_mute=ignore_mute,
                    ),
                )
            message_list = resolved_messages

        if max_concurrency is None or max_concurrency <= 1:
            items: list[BulkReplyItemResult] = []
            for message in message_list:
                try:
                    await self.reply(message=message)
                except Exception as exc:
                    items.append(BulkReplyItemResult(message=message, error=exc))
                else:
                    items.append(BulkReplyItemResult(message=message))
            return BulkReplyResult(items=items)

        semaphore = asyncio.Semaphore(max_concurrency)

        async def _run(message: ReplyMessage) -> BulkReplyItemResult:
            async with semaphore:
                try:
                    await self.reply(message=message)
                except Exception as exc:
                    return BulkReplyItemResult(message=message, error=exc)
                return BulkReplyItemResult(message=message)

        results = await asyncio.gather(*(_run(message) for message in message_list))
        return BulkReplyResult(items=list(results))

    async def reply_message(
        self,
        *,
        bot_id: UUID,
        sync_id: UUID,
        body: str,
        metadata: Missing[dict[str, Any]] = Undefined,
        bubbles: Missing[BubbleMarkup] = Undefined,
        keyboard: Missing[KeyboardMarkup] = Undefined,
        file: Missing[IncomingFileAttachment | OutgoingAttachment] = Undefined,
        silent_response: Missing[bool] = Undefined,
        markup_auto_adjust: Missing[bool] = Undefined,
        stealth_mode: Missing[bool] = Undefined,
        send_push: Missing[bool] = Undefined,
        ignore_mute: Missing[bool] = Undefined,
        options: MessageOptions | None = None,
    ) -> None:
        """Reply on message by `sync_id`.

        :param bot_id: Bot which should perform the request.
        :param sync_id: `sync_id` of message to reply on.
        :param body: Reply body.
        :param metadata: Notification options.
        :param bubbles: Bubbles (buttons attached to message) markup.
        :param keyboard: Keyboard (buttons below message input) markup.
        :param file: Attachment.
        :param silent_response: (BotX default: False) Exclude next user
            messages from history.
        :param markup_auto_adjust: (BotX default: False) Move button to next
            row, if its text doesn't fit.
        :param stealth_mode: (BotX default: False) Enable stealth mode.
        :param send_push: (BotX default: True) Send push notification on
            devices.
        :param ignore_mute: (BotX default: False) Ignore mute or dnd (do not
            disturb).
        """
        (
            _recipients,
            silent_response,
            markup_auto_adjust,
            stealth_mode,
            send_push,
            ignore_mute,
        ) = resolve_message_options(
            options,
            silent_response=silent_response,
            markup_auto_adjust=markup_auto_adjust,
            stealth_mode=stealth_mode,
            send_push=send_push,
            ignore_mute=ignore_mute,
        )

        await self._botx_api.reply_message(
            bot_id=bot_id,
            sync_id=sync_id,
            body=body,
            metadata=metadata,
            bubbles=bubbles,
            keyboard=keyboard,
            file=file,
            silent_response=silent_response,
            markup_auto_adjust=markup_auto_adjust,
            stealth_mode=stealth_mode,
            send_push=send_push,
            ignore_mute=ignore_mute,
        )

    async def reply_to(
        self,
        message: IncomingMessage,
        *,
        body: str,
        metadata: Missing[dict[str, Any]] = Undefined,
        bubbles: Missing[BubbleMarkup] = Undefined,
        keyboard: Missing[KeyboardMarkup] = Undefined,
        file: Missing[IncomingFileAttachment | OutgoingAttachment] = Undefined,
        silent_response: Missing[bool] = Undefined,
        markup_auto_adjust: Missing[bool] = Undefined,
        stealth_mode: Missing[bool] = Undefined,
        send_push: Missing[bool] = Undefined,
        ignore_mute: Missing[bool] = Undefined,
        options: MessageOptions | None = None,
    ) -> None:
        """Reply on incoming message without passing explicit ids."""
        await self.reply_message(
            bot_id=message.bot.id,
            sync_id=message.sync_id,
            body=body,
            metadata=metadata,
            bubbles=bubbles,
            keyboard=keyboard,
            file=file,
            silent_response=silent_response,
            markup_auto_adjust=markup_auto_adjust,
            stealth_mode=stealth_mode,
            send_push=send_push,
            ignore_mute=ignore_mute,
            options=options,
        )

    async def get_message_status(
        self,
        *,
        bot_id: UUID,
        sync_id: UUID,
    ) -> MessageStatus:
        """
        Get status of message by `sync_id`.

        :param bot_id: Bot which should perform the request.
        :param sync_id: `sync_id` of message to get its status.

        :returns: Message status object.
        """
        return await self._botx_api.get_message_status(
            bot_id=bot_id,
            sync_id=sync_id,
        )

    async def start_typing(
        self,
        *,
        bot_id: UUID,
        chat_id: UUID,
    ) -> None:
        """Send `typing` event.

        :param bot_id: Bot which should perform the request.
        :param chat_id: Target chat id.
        """
        await self._botx_api.start_typing(bot_id=bot_id, chat_id=chat_id)

    async def stop_typing(
        self,
        *,
        bot_id: UUID,
        chat_id: UUID,
    ) -> None:
        """Send `stop_typing` event.

        :param bot_id: Bot which should perform the request.
        :param chat_id: Target chat id.
        """
        await self._botx_api.stop_typing(bot_id=bot_id, chat_id=chat_id)

    async def delete_message(
        self,
        *,
        bot_id: UUID,
        sync_id: UUID,
    ) -> None:
        """Delete message.

        :param bot_id: Bot which should perform the request.
        :param sync_id: Target sync_id.
        """
        await self._botx_api.delete_message(bot_id=bot_id, sync_id=sync_id)

    async def edit_from(
        self,
        message: IncomingMessage,
        *,
        body: Missing[str] = Undefined,
        metadata: Missing[dict[str, Any]] = Undefined,
        bubbles: Missing[BubbleMarkup] = Undefined,
        keyboard: Missing[KeyboardMarkup] = Undefined,
        file: MissingOptionalAttachment = Undefined,
        markup_auto_adjust: Missing[bool] = Undefined,
        options: MessageOptions | None = None,
    ) -> None:
        """Edit message by incoming source_sync_id without passing explicit ids."""
        if message.source_sync_id is None:
            raise ValueError("Incoming message has no source_sync_id")

        await self.edit_message(
            bot_id=message.bot.id,
            sync_id=message.source_sync_id,
            body=body,
            metadata=metadata,
            bubbles=bubbles,
            keyboard=keyboard,
            file=file,
            markup_auto_adjust=markup_auto_adjust,
            options=options,
        )
