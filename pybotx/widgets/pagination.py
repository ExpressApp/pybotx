import asyncio
from copy import deepcopy
from typing import Any
from uuid import UUID

from pybotx.models.message.markup import BubbleMarkup, KeyboardMarkup
from pybotx.models.message.outgoing_message import OutgoingMessage

from . import strings
from .base import (
    PYBOTX_WIDGET_FLAG,
    Widget,
    build_outgoing_message_from_incoming,
    outgoing_markup,
)
from .markup import merge_message_markup

START_FROM_KEY = "pagination_start_from"
MESSAGE_IDS_KEY = "pagination_message_ids"


def _pagination_label(left_num: int, right_num: int, *, backward: bool) -> str:
    arrow = strings.LEFT_ARROW if backward else strings.RIGHT_ARROW
    direction = "Назад к" if backward else "Вперёд к"
    if left_num == right_num:
        range_label = str(left_num)
    else:
        range_label = f"{left_num}-{right_num}"
    return f"{arrow} {direction} [{range_label}]"


def _safe_int(value: object, default: int) -> int:
    if isinstance(value, int):
        return value
    if isinstance(value, str) and value.isdigit():
        return int(value)
    return default


def _to_uuid_list(value: object) -> list[UUID]:
    if not isinstance(value, list):
        return []

    uuids: list[UUID] = []
    for message_id in value:
        try:
            uuids.append(UUID(str(message_id)))
        except ValueError:
            continue
    return uuids


class PaginationWidget(Widget):
    def __init__(
        self,
        widget_content: list[OutgoingMessage | str],
        paginate_by: int,
        delay_between_messages: float = 0.5,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)

        if paginate_by <= 0:
            raise ValueError("'paginate_by' should be greater than 0")

        if delay_between_messages < 0:
            raise ValueError("'delay_between_messages' should be non-negative")

        self.widget_content = [
            self._normalize_widget_message(content_item) for content_item in widget_content
        ]
        self.paginate_by = paginate_by
        self.delay_between_messages = delay_between_messages

        self.content_len = len(self.widget_content)
        self.start_from = _safe_int(self.message.data.get(START_FROM_KEY), default=0)
        if self.start_from < 0:
            self.start_from = 0

        self.message_ids = _to_uuid_list(self.message.metadata.get(MESSAGE_IDS_KEY))
        self.empty_msg = build_outgoing_message_from_incoming(
            message=self.message,
            body=strings.EMPTY_MSG_SYMBOL,
            bubbles=BubbleMarkup(),
            keyboard=KeyboardMarkup(),
        )

    @property
    def display_content(self) -> list[OutgoingMessage]:
        return self.widget_content[self.start_from : self.start_from + self.paginate_by]

    def add_markup(self) -> None:
        if self.content_len > self.paginate_by:
            self.add_backward_btn()
            self.add_forward_btn()
        self.add_additional_markup()

    async def send_widget_message(self) -> None:
        if self.message_ids:
            await self._update_widget_messages()
        else:
            await self._send_new_widget_messages()

    def add_backward_btn(self) -> None:
        if self.start_from < self.paginate_by:
            return

        left_border = self.start_from - self.paginate_by
        label = _pagination_label(
            left_num=left_border + 1,
            right_num=self.start_from,
            backward=True,
        )
        self.widget_bubbles.add_button(
            label=label,
            command=self.command,
            data={START_FROM_KEY: left_border},
        )

    def add_forward_btn(self) -> None:
        left_border = self.start_from + self.paginate_by
        if left_border >= self.content_len:
            return

        right_border = min(left_border + self.paginate_by, self.content_len)
        label = _pagination_label(
            left_num=left_border + 1,
            right_num=right_border,
            backward=False,
        )
        self.widget_bubbles.add_button(
            label=label,
            command=self.command,
            data={START_FROM_KEY: left_border},
            new_row=False,
        )

    async def _send_new_widget_messages(self) -> None:
        display_content = self.display_content
        if not display_content:
            return

        for widget_message in display_content[:-1]:
            message_id = await self.bot.send(message=widget_message)
            self.message_ids.append(message_id)
            await asyncio.sleep(self.delay_between_messages)

        last_widget_message = display_content[-1]
        self._prepare_last_message(last_widget_message)
        await self.send_or_update_message(last_widget_message)

    async def _update_widget_messages(self) -> None:
        display_content = self.display_content

        for index in range(self.paginate_by - 1):
            if index >= len(self.message_ids):
                break

            message_to_send = self.empty_msg
            if index < len(display_content):
                message_to_send = display_content[index]

            await self._edit_widget_message(self.message_ids[index], message_to_send)
            await asyncio.sleep(self.delay_between_messages)

        last_item_idx = self.paginate_by - 1
        last_widget_message = self.empty_msg
        if last_item_idx < len(display_content):
            last_widget_message = display_content[last_item_idx]

        self._prepare_last_message(last_widget_message)

        if self.message.source_sync_id is None:
            await self.bot.send(message=last_widget_message)
            return

        await self._edit_widget_message(self.message.source_sync_id, last_widget_message)

    async def _edit_widget_message(
        self,
        sync_id: UUID,
        widget_message: OutgoingMessage,
    ) -> None:
        await self.bot.edit_message(
            bot_id=widget_message.bot_id,
            sync_id=sync_id,
            body=widget_message.body,
            metadata=widget_message.metadata,
            bubbles=widget_message.bubbles,
            keyboard=widget_message.keyboard,
            file=widget_message.file,
            markup_auto_adjust=widget_message.markup_auto_adjust,
        )

    def _prepare_last_message(self, message: OutgoingMessage) -> None:
        merged_markup = merge_message_markup(
            outgoing_markup(message),
            outgoing_markup(self.widget_message),
        )
        message.bubbles = merged_markup.bubbles
        message.keyboard = merged_markup.keyboard

        metadata = {}
        if message.metadata:
            metadata = dict(message.metadata)
        metadata[MESSAGE_IDS_KEY] = [str(message_id) for message_id in self.message_ids]
        metadata[PYBOTX_WIDGET_FLAG] = 1
        message.metadata = metadata

    def _normalize_widget_message(
        self,
        content_item: OutgoingMessage | str,
    ) -> OutgoingMessage:
        if isinstance(content_item, OutgoingMessage):
            item = deepcopy(content_item)
            item.bot_id = self.message.bot.id
            item.chat_id = self.message.chat.id
            return item

        return build_outgoing_message_from_incoming(
            message=self.message,
            body=str(content_item),
        )
