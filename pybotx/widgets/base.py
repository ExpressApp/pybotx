from abc import ABC, abstractmethod
from typing import Any, Literal, cast

from pybotx.bot.bot import Bot
from pybotx.missing import Missing, Undefined
from pybotx.models.attachments import IncomingFileAttachment, OutgoingAttachment
from pybotx.models.message.incoming_message import IncomingMessage
from pybotx.models.message.markup import BubbleMarkup, KeyboardMarkup
from pybotx.models.message.outgoing_message import OutgoingMessage

from .markup import MessageMarkup, merge_message_markup

PYBOTX_WIDGET_FLAG = "pybotx_widget"
PYBOTX_WIDGET_RESULT_MODE_KEY = "pybotx_widget_result_mode"
WIDGET_RESULT_MODE_EDIT: Literal["edit"] = "edit"
WIDGET_RESULT_MODE_MESSAGE: Literal["message"] = "message"
WidgetResultMode = Literal["edit", "message"]


def _normalize_result_mode(value: object) -> WidgetResultMode | None:
    if not isinstance(value, str):
        return None

    normalized = value.strip().lower()
    if normalized in {"edit", "inline", "update"}:
        return WIDGET_RESULT_MODE_EDIT

    if normalized in {"message", "reply", "send"}:
        return WIDGET_RESULT_MODE_MESSAGE

    return None


def _parse_result_mode_from_argument(argument: str) -> WidgetResultMode | None:
    for token in argument.split():
        if parsed_mode := _normalize_result_mode(token):
            return parsed_mode

        normalized_token = token.strip().lower()
        for prefix in ("mode=", "result=", "--mode=", "--result="):
            if not normalized_token.startswith(prefix):
                continue

            raw_mode = normalized_token.split("=", 1)[1]
            return _normalize_result_mode(raw_mode)

    return None


def build_outgoing_message_from_incoming(
    *,
    message: IncomingMessage,
    body: str,
    metadata: Missing[dict[str, Any]] = Undefined,
    bubbles: Missing[BubbleMarkup] = Undefined,
    keyboard: Missing[KeyboardMarkup] = Undefined,
    file: Missing[IncomingFileAttachment | OutgoingAttachment] = Undefined,
) -> OutgoingMessage:
    return OutgoingMessage(
        bot_id=message.bot.id,
        chat_id=message.chat.id,
        body=body,
        metadata=metadata,
        bubbles=bubbles,
        keyboard=keyboard,
        file=file,
    )


def outgoing_markup(message: OutgoingMessage) -> MessageMarkup:
    bubbles = ensure_widget_bubbles(message)
    keyboard = ensure_widget_keyboard(message)
    return MessageMarkup(
        bubbles=bubbles,
        keyboard=keyboard,
    )


def ensure_widget_bubbles(message: OutgoingMessage) -> BubbleMarkup:
    if message.bubbles is Undefined:
        message.bubbles = BubbleMarkup()

    return cast(BubbleMarkup, message.bubbles)


def ensure_widget_keyboard(message: OutgoingMessage) -> KeyboardMarkup:
    if message.keyboard is Undefined:
        message.keyboard = KeyboardMarkup()

    return cast(KeyboardMarkup, message.keyboard)


def ensure_widget_metadata(message: OutgoingMessage) -> dict[str, Any]:
    if message.metadata is Undefined:
        message.metadata = {}

    return cast(dict[str, Any], message.metadata)


class Widget(ABC):
    widget_message: OutgoingMessage

    def __init__(
        self,
        *,
        message: IncomingMessage,
        bot: Bot,
        command: str,
        additional_markup: MessageMarkup | None = None,
        result_mode: WidgetResultMode | None = None,
    ) -> None:
        self.message = message
        self.bot = bot
        self.command = command
        self.additional_markup = additional_markup

        self.widget_message = build_outgoing_message_from_incoming(
            message=message,
            body="",
            metadata=dict(message.metadata),
            bubbles=BubbleMarkup(),
            keyboard=KeyboardMarkup(),
        )
        self.result_mode = self._resolve_result_mode(result_mode)
        self.widget_metadata[PYBOTX_WIDGET_RESULT_MODE_KEY] = self.result_mode

    @property
    def widget_bubbles(self) -> BubbleMarkup:
        return ensure_widget_bubbles(self.widget_message)

    @property
    def widget_keyboard(self) -> KeyboardMarkup:
        return ensure_widget_keyboard(self.widget_message)

    @property
    def widget_metadata(self) -> dict[str, Any]:
        return ensure_widget_metadata(self.widget_message)

    @abstractmethod
    def add_markup(self) -> None:
        raise NotImplementedError

    def add_additional_markup(self) -> None:
        if self.additional_markup is None:
            return

        current_markup = outgoing_markup(self.widget_message)
        merged_markup = merge_message_markup(current_markup, self.additional_markup)
        self.widget_message.bubbles = merged_markup.bubbles
        self.widget_message.keyboard = merged_markup.keyboard

    async def send_widget_message(self) -> None:
        await self.send_or_update_message(self.widget_message)

    async def send_result(
        self,
        body: str,
        markup: MessageMarkup | None = None,
    ) -> None:
        markup = markup or MessageMarkup()

        if self.result_mode == WIDGET_RESULT_MODE_MESSAGE:
            await self.bot.answer_message(
                body,
                metadata={PYBOTX_WIDGET_RESULT_MODE_KEY: self.result_mode},
                bubbles=markup.bubbles,
                keyboard=markup.keyboard,
            )
            return

        await self.send_or_update_message(
            build_outgoing_message_from_incoming(
                message=self.message,
                body=body,
                metadata={
                    **dict(self.message.metadata),
                    PYBOTX_WIDGET_RESULT_MODE_KEY: self.result_mode,
                },
                bubbles=markup.bubbles,
                keyboard=markup.keyboard,
            ),
        )

    async def display(self) -> None:
        self.add_markup()
        await self.send_widget_message()

    async def send_or_update_message(self, widget_message: OutgoingMessage) -> None:
        widget_message.metadata = self._build_widget_metadata(widget_message.metadata)

        if self._is_widget_update():
            assert self.message.source_sync_id is not None
            await self.bot.edit_message(
                bot_id=self.message.bot.id,
                sync_id=self.message.source_sync_id,
                body=widget_message.body,
                metadata=widget_message.metadata,
                bubbles=widget_message.bubbles,
                keyboard=widget_message.keyboard,
                file=widget_message.file,
                markup_auto_adjust=widget_message.markup_auto_adjust,
            )
            return

        await self.bot.send(message=widget_message)

    def _build_widget_metadata(
        self,
        metadata: Missing[dict[str, Any]],
    ) -> dict[str, Any]:
        widget_metadata: dict[str, Any]
        if metadata is Undefined:
            widget_metadata = dict(self.message.metadata)
        else:
            widget_metadata = dict(cast(dict[str, Any], metadata))

        widget_metadata[PYBOTX_WIDGET_FLAG] = 1
        return widget_metadata

    def _is_widget_update(self) -> bool:
        return bool(
            self.message.metadata.get(PYBOTX_WIDGET_FLAG)
            and self.message.source_sync_id is not None
        )

    def _resolve_result_mode(
        self,
        result_mode: WidgetResultMode | None,
    ) -> WidgetResultMode:
        if result_mode is not None:
            return result_mode

        if metadata_mode := _normalize_result_mode(
            self.message.metadata.get(PYBOTX_WIDGET_RESULT_MODE_KEY),
        ):
            return metadata_mode

        if argument_mode := _parse_result_mode_from_argument(self.message.argument):
            return argument_mode

        return WIDGET_RESULT_MODE_EDIT
