from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from uuid import UUID

from pybotx.domain.missing import Missing, Undefined
from pybotx.domain.models.attachments import IncomingFileAttachment, OutgoingAttachment
from pybotx.domain.models.message.incoming_message import IncomingMessage
from pybotx.domain.models.message.markup import BubbleMarkup, KeyboardMarkup
from pybotx.domain.models.message.message_options import MessageOptions
from pybotx.domain.models.message.outgoing_message import OutgoingMessage
from pybotx.domain.models.message.reply_message import ReplyMessage
from pybotx.domain.models.message.edit_message import EditMessage


@dataclass(slots=True)
class OutgoingMessageBuilder:
    bot_id: UUID
    chat_id: UUID
    body: str
    metadata: Missing[dict[str, Any]] = Undefined
    bubbles: Missing[BubbleMarkup] = Undefined
    keyboard: Missing[KeyboardMarkup] = Undefined
    file: Missing[IncomingFileAttachment | OutgoingAttachment] = Undefined
    recipients: Missing[list[UUID]] = Undefined
    silent_response: Missing[bool] = Undefined
    markup_auto_adjust: Missing[bool] = Undefined
    stealth_mode: Missing[bool] = Undefined
    send_push: Missing[bool] = Undefined
    ignore_mute: Missing[bool] = Undefined

    @classmethod
    def for_incoming(
        cls,
        message: IncomingMessage,
        *,
        body: str,
    ) -> "OutgoingMessageBuilder":
        return cls(
            bot_id=message.bot.id,
            chat_id=message.chat.id,
            body=body,
        )

    def with_metadata(self, metadata: dict[str, Any]) -> "OutgoingMessageBuilder":
        self.metadata = metadata
        return self

    def with_bubbles(self, bubbles: BubbleMarkup) -> "OutgoingMessageBuilder":
        self.bubbles = bubbles
        return self

    def with_keyboard(self, keyboard: KeyboardMarkup) -> "OutgoingMessageBuilder":
        self.keyboard = keyboard
        return self

    def with_file(
        self,
        file: IncomingFileAttachment | OutgoingAttachment,
    ) -> "OutgoingMessageBuilder":
        self.file = file
        return self

    def to_recipients(self, recipients: list[UUID]) -> "OutgoingMessageBuilder":
        self.recipients = recipients
        return self

    def with_options(self, options: MessageOptions) -> "OutgoingMessageBuilder":
        self.recipients = options.recipients
        self.silent_response = options.silent_response
        self.markup_auto_adjust = options.markup_auto_adjust
        self.stealth_mode = options.stealth_mode
        self.send_push = options.send_push
        self.ignore_mute = options.ignore_mute
        return self

    def silent(self) -> "OutgoingMessageBuilder":
        self.silent_response = True
        return self

    def auto_adjust_buttons(self) -> "OutgoingMessageBuilder":
        self.markup_auto_adjust = True
        return self

    def stealth(self) -> "OutgoingMessageBuilder":
        self.stealth_mode = True
        return self

    def no_push(self) -> "OutgoingMessageBuilder":
        self.send_push = False
        return self

    def force_notification(self) -> "OutgoingMessageBuilder":
        self.ignore_mute = True
        return self

    def build(self) -> OutgoingMessage:
        return OutgoingMessage(
            bot_id=self.bot_id,
            chat_id=self.chat_id,
            body=self.body,
            metadata=self.metadata,
            bubbles=self.bubbles,
            keyboard=self.keyboard,
            file=self.file,
            recipients=self.recipients,
            silent_response=self.silent_response,
            markup_auto_adjust=self.markup_auto_adjust,
            stealth_mode=self.stealth_mode,
            send_push=self.send_push,
            ignore_mute=self.ignore_mute,
        )

@dataclass(slots=True)
class ReplyMessageBuilder:
    bot_id: UUID
    sync_id: UUID
    body: str
    metadata: Missing[dict[str, Any]] = Undefined
    bubbles: Missing[BubbleMarkup] = Undefined
    keyboard: Missing[KeyboardMarkup] = Undefined
    file: Missing[IncomingFileAttachment | OutgoingAttachment] = Undefined
    silent_response: Missing[bool] = Undefined
    markup_auto_adjust: Missing[bool] = Undefined
    stealth_mode: Missing[bool] = Undefined
    send_push: Missing[bool] = Undefined
    ignore_mute: Missing[bool] = Undefined

    @classmethod
    def for_incoming(
        cls,
        message: IncomingMessage,
        *,
        body: str,
        sync_id: UUID,
    ) -> "ReplyMessageBuilder":
        return cls(
            bot_id=message.bot.id,
            sync_id=sync_id,
            body=body,
        )

    @classmethod
    def for_incoming_message(
        cls,
        message: IncomingMessage,
        *,
        body: str,
    ) -> "ReplyMessageBuilder":
        return cls(
            bot_id=message.bot.id,
            sync_id=message.sync_id,
            body=body,
        )

    def with_metadata(self, metadata: dict[str, Any]) -> "ReplyMessageBuilder":
        self.metadata = metadata
        return self

    def with_bubbles(self, bubbles: BubbleMarkup) -> "ReplyMessageBuilder":
        self.bubbles = bubbles
        return self

    def with_keyboard(self, keyboard: KeyboardMarkup) -> "ReplyMessageBuilder":
        self.keyboard = keyboard
        return self

    def with_file(
        self,
        file: IncomingFileAttachment | OutgoingAttachment,
    ) -> "ReplyMessageBuilder":
        self.file = file
        return self

    def with_options(self, options: MessageOptions) -> "ReplyMessageBuilder":
        self.silent_response = options.silent_response
        self.markup_auto_adjust = options.markup_auto_adjust
        self.stealth_mode = options.stealth_mode
        self.send_push = options.send_push
        self.ignore_mute = options.ignore_mute
        return self

    def silent(self) -> "ReplyMessageBuilder":
        self.silent_response = True
        return self

    def auto_adjust_buttons(self) -> "ReplyMessageBuilder":
        self.markup_auto_adjust = True
        return self

    def stealth(self) -> "ReplyMessageBuilder":
        self.stealth_mode = True
        return self

    def no_push(self) -> "ReplyMessageBuilder":
        self.send_push = False
        return self

    def force_notification(self) -> "ReplyMessageBuilder":
        self.ignore_mute = True
        return self

    def build(self) -> ReplyMessage:
        return ReplyMessage(
            bot_id=self.bot_id,
            sync_id=self.sync_id,
            body=self.body,
            metadata=self.metadata,
            bubbles=self.bubbles,
            keyboard=self.keyboard,
            file=self.file,
            silent_response=self.silent_response,
            markup_auto_adjust=self.markup_auto_adjust,
            stealth_mode=self.stealth_mode,
            send_push=self.send_push,
            ignore_mute=self.ignore_mute,
        )


@dataclass(slots=True)
class EditMessageBuilder:
    bot_id: UUID
    sync_id: UUID
    body: Missing[str] = Undefined
    metadata: Missing[dict[str, Any]] = Undefined
    bubbles: Missing[BubbleMarkup] = Undefined
    keyboard: Missing[KeyboardMarkup] = Undefined
    file: Missing[IncomingFileAttachment | OutgoingAttachment] = Undefined
    markup_auto_adjust: Missing[bool] = Undefined

    def with_body(self, body: str) -> "EditMessageBuilder":
        self.body = body
        return self

    @classmethod
    def for_incoming_source(
        cls,
        message: IncomingMessage,
        *,
        sync_id: UUID,
    ) -> "EditMessageBuilder":
        return cls(
            bot_id=message.bot.id,
            sync_id=sync_id,
        )

    @classmethod
    def for_incoming_source_id(
        cls,
        message: IncomingMessage,
    ) -> "EditMessageBuilder":
        if message.source_sync_id is None:
            raise ValueError("Incoming message has no source_sync_id")

        return cls(
            bot_id=message.bot.id,
            sync_id=message.source_sync_id,
        )

    def clear_body(self) -> "EditMessageBuilder":
        self.body = ""
        return self

    def with_metadata(self, metadata: dict[str, Any]) -> "EditMessageBuilder":
        self.metadata = metadata
        return self

    def clear_metadata(self) -> "EditMessageBuilder":
        self.metadata = {}
        return self

    def with_bubbles(self, bubbles: BubbleMarkup) -> "EditMessageBuilder":
        self.bubbles = bubbles
        return self

    def clear_bubbles(self) -> "EditMessageBuilder":
        self.bubbles = None
        return self

    def with_keyboard(self, keyboard: KeyboardMarkup) -> "EditMessageBuilder":
        self.keyboard = keyboard
        return self

    def clear_keyboard(self) -> "EditMessageBuilder":
        self.keyboard = None
        return self

    def with_file(
        self,
        file: IncomingFileAttachment | OutgoingAttachment,
    ) -> "EditMessageBuilder":
        self.file = file
        return self

    def clear_file(self) -> "EditMessageBuilder":
        self.file = None
        return self

    def auto_adjust_buttons(self) -> "EditMessageBuilder":
        self.markup_auto_adjust = True
        return self

    def build(self) -> EditMessage:
        return EditMessage(
            bot_id=self.bot_id,
            sync_id=self.sync_id,
            body=self.body,
            metadata=self.metadata,
            bubbles=self.bubbles,
            keyboard=self.keyboard,
            file=self.file,
            markup_auto_adjust=self.markup_auto_adjust,
        )


__all__ = (
    "OutgoingMessageBuilder",
    "ReplyMessageBuilder",
    "EditMessageBuilder",
)
