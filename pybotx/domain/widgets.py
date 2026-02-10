from __future__ import annotations

from dataclasses import dataclass
from math import ceil
from typing import Any, Callable, Sequence
from uuid import UUID

from pybotx.domain.errors import InvalidWidgetPayloadError
from pybotx.domain.missing import Missing, Undefined
from pybotx.domain.models.message.edit_message import EditMessage
from pybotx.domain.models.message.incoming_message import IncomingMessage
from pybotx.domain.models.message.markup import BubbleMarkup
from pybotx.domain.models.message.outgoing_message import OutgoingMessage


DEFAULT_PREV_LABEL = "Назад"
DEFAULT_NEXT_LABEL = "Вперед"
DEFAULT_EMPTY_TEXT = "Конец списка"


def _parse_int(value: Any, *, field_name: str) -> int:
    if isinstance(value, bool):
        raise InvalidWidgetPayloadError(
            f"{field_name} must be an integer, got bool",
        )
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        try:
            return int(value)
        except ValueError as exc:
            raise InvalidWidgetPayloadError(
                f"{field_name} must be an integer string",
            ) from exc
    raise InvalidWidgetPayloadError(f"{field_name} must be an integer")


def _ensure_list(value: Any, *, field_name: str) -> list[Any]:
    if not isinstance(value, list):
        raise InvalidWidgetPayloadError(f"{field_name} must be a list")
    return value


def _ensure_source_sync_id(message: IncomingMessage) -> UUID:
    if message.source_sync_id is None:
        raise InvalidWidgetPayloadError("Widget command has no source_sync_id")
    return message.source_sync_id


def _build_bubbles(
    *,
    command: str,
    prev_label: str,
    next_label: str,
    prev_data: dict[str, Any] | None,
    next_data: dict[str, Any] | None,
) -> BubbleMarkup:
    bubbles = BubbleMarkup()
    if prev_data is not None:
        bubbles.add_button(
            label=prev_label,
            command=command,
            data=prev_data,
            new_row=True,
        )
    if next_data is not None:
        bubbles.add_button(
            label=next_label,
            command=command,
            data=next_data,
            new_row=prev_data is None,
        )
    return bubbles


@dataclass(slots=True)
class SingleMessageWidget:
    command: str
    render_item: Callable[[Any], str] = str
    prev_label: str = DEFAULT_PREV_LABEL
    next_label: str = DEFAULT_NEXT_LABEL
    elems_key: str = "elems"
    index_key: str = "current_index"
    include_state_in_metadata: bool = False

    def __post_init__(self) -> None:
        if not isinstance(self.command, str):
            raise InvalidWidgetPayloadError("command must be a string")
        if not callable(self.render_item):
            raise InvalidWidgetPayloadError("render_item must be callable")
        if not isinstance(self.prev_label, str):
            raise InvalidWidgetPayloadError("prev_label must be a string")
        if not isinstance(self.next_label, str):
            raise InvalidWidgetPayloadError("next_label must be a string")
        if not isinstance(self.elems_key, str):
            raise InvalidWidgetPayloadError("elems_key must be a string")
        if not isinstance(self.index_key, str):
            raise InvalidWidgetPayloadError("index_key must be a string")

    def render(
        self,
        *,
        elems: Sequence[Any],
        current_index: int,
    ) -> tuple[str, dict[str, Any], BubbleMarkup]:
        if not elems:
            raise InvalidWidgetPayloadError("Widget elems are empty")
        if current_index < 0 or current_index >= len(elems):
            raise InvalidWidgetPayloadError("current_index is out of range")

        body = str(self.render_item(elems[current_index]))
        metadata = {self.elems_key: list(elems)}
        if self.include_state_in_metadata:
            metadata[self.index_key] = current_index

        prev_data = None
        if current_index > 0:
            prev_data = {self.index_key: current_index - 1}
        next_data = None
        if current_index < len(elems) - 1:
            next_data = {self.index_key: current_index + 1}

        bubbles = _build_bubbles(
            command=self.command,
            prev_label=self.prev_label,
            next_label=self.next_label,
            prev_data=prev_data,
            next_data=next_data,
        )
        return body, metadata, bubbles

    def build_outgoing(
        self,
        *,
        bot_id: UUID,
        chat_id: UUID,
        elems: Sequence[Any],
        current_index: int = 0,
    ) -> OutgoingMessage:
        body, metadata, bubbles = self.render(elems=elems, current_index=current_index)
        return OutgoingMessage(
            bot_id=bot_id,
            chat_id=chat_id,
            body=body,
            metadata=metadata,
            bubbles=bubbles,
        )

    def build_edit(
        self,
        *,
        bot_id: UUID,
        sync_id: UUID,
        elems: Sequence[Any],
        current_index: int,
    ) -> EditMessage:
        body, metadata, bubbles = self.render(elems=elems, current_index=current_index)
        return EditMessage(
            bot_id=bot_id,
            sync_id=sync_id,
            body=body,
            metadata=metadata,
            bubbles=bubbles,
        )

    def build_edit_from_message(self, message: IncomingMessage) -> EditMessage:
        if self.index_key not in message.data:
            raise InvalidWidgetPayloadError(f"{self.index_key} is missing in data")
        if self.elems_key not in message.metadata:
            raise InvalidWidgetPayloadError(f"{self.elems_key} is missing in metadata")

        current_index = _parse_int(message.data[self.index_key], field_name=self.index_key)
        elems = _ensure_list(message.metadata[self.elems_key], field_name=self.elems_key)
        sync_id = _ensure_source_sync_id(message)

        return self.build_edit(
            bot_id=message.bot.id,
            sync_id=sync_id,
            elems=elems,
            current_index=current_index,
        )


@dataclass(slots=True)
class MultiMessageWidget:
    command: str
    page_size: int
    render_item: Callable[[Any], str] = str
    prev_label: str = DEFAULT_PREV_LABEL
    next_label: str = DEFAULT_NEXT_LABEL
    empty_text: str = DEFAULT_EMPTY_TEXT
    elems_key: str = "elems"
    sync_ids_key: str = "sync_ids"
    page_key: str = "page"
    include_state_in_metadata: bool = False

    def __post_init__(self) -> None:
        if self.page_size <= 0:
            raise InvalidWidgetPayloadError("page_size must be positive")
        if not isinstance(self.command, str):
            raise InvalidWidgetPayloadError("command must be a string")
        if not callable(self.render_item):
            raise InvalidWidgetPayloadError("render_item must be callable")
        if not isinstance(self.prev_label, str):
            raise InvalidWidgetPayloadError("prev_label must be a string")
        if not isinstance(self.next_label, str):
            raise InvalidWidgetPayloadError("next_label must be a string")
        if not isinstance(self.empty_text, str):
            raise InvalidWidgetPayloadError("empty_text must be a string")
        if not isinstance(self.elems_key, str):
            raise InvalidWidgetPayloadError("elems_key must be a string")
        if not isinstance(self.sync_ids_key, str):
            raise InvalidWidgetPayloadError("sync_ids_key must be a string")
        if not isinstance(self.page_key, str):
            raise InvalidWidgetPayloadError("page_key must be a string")

    def _total_pages(self, elems: Sequence[Any]) -> int:
        return max(1, ceil(len(elems) / self.page_size))

    def _build_metadata(
        self,
        *,
        elems: Sequence[Any],
        sync_ids: Sequence[UUID],
        page: int,
    ) -> dict[str, Any]:
        metadata = {
            self.elems_key: list(elems),
            self.sync_ids_key: [str(sync_id) for sync_id in sync_ids],
        }
        if self.include_state_in_metadata:
            metadata[self.page_key] = page
        return metadata

    def _build_page_bubbles(self, *, page: int, total_pages: int) -> BubbleMarkup:
        prev_data = None
        if page > 0:
            prev_data = {self.page_key: page - 1}
        next_data = None
        if page < total_pages - 1:
            next_data = {self.page_key: page + 1}

        return _build_bubbles(
            command=self.command,
            prev_label=self.prev_label,
            next_label=self.next_label,
            prev_data=prev_data,
            next_data=next_data,
        )

    def _render_body(self, elem: Any | None) -> str:
        if elem is None:
            return self.empty_text
        return str(self.render_item(elem))

    def _page_items(self, elems: Sequence[Any], page: int) -> list[Any | None]:
        total_pages = self._total_pages(elems)
        if page < 0 or page >= total_pages:
            raise InvalidWidgetPayloadError("page is out of range")

        start = page * self.page_size
        items: list[Any | None] = []
        for idx in range(self.page_size):
            item_index = start + idx
            if item_index < len(elems):
                items.append(elems[item_index])
            else:
                items.append(None)
        return items

    def build_outgoing_head_messages(
        self,
        *,
        bot_id: UUID,
        chat_id: UUID,
        elems: Sequence[Any],
        page: int = 0,
    ) -> list[OutgoingMessage]:
        items = self._page_items(elems, page)
        head_items = items[: max(self.page_size - 1, 0)]
        messages: list[OutgoingMessage] = []
        for elem in head_items:
            messages.append(
                OutgoingMessage(
                    bot_id=bot_id,
                    chat_id=chat_id,
                    body=self._render_body(elem),
                )
            )
        return messages

    def build_outgoing_tail_message(
        self,
        *,
        bot_id: UUID,
        chat_id: UUID,
        elems: Sequence[Any],
        page: int,
        sync_ids: Sequence[UUID],
    ) -> OutgoingMessage:
        expected_sync_ids = max(self.page_size - 1, 0)
        if len(sync_ids) != expected_sync_ids:
            raise InvalidWidgetPayloadError("sync_ids length does not match page_size")

        items = self._page_items(elems, page)
        last_elem = items[-1] if items else None
        metadata = self._build_metadata(elems=elems, sync_ids=sync_ids, page=page)
        bubbles = self._build_page_bubbles(page=page, total_pages=self._total_pages(elems))

        return OutgoingMessage(
            bot_id=bot_id,
            chat_id=chat_id,
            body=self._render_body(last_elem),
            metadata=metadata,
            bubbles=bubbles,
        )

    def build_edit_from_message(self, message: IncomingMessage) -> list[EditMessage]:
        if self.page_key not in message.data:
            raise InvalidWidgetPayloadError(f"{self.page_key} is missing in data")
        if self.elems_key not in message.metadata:
            raise InvalidWidgetPayloadError(f"{self.elems_key} is missing in metadata")

        page = _parse_int(message.data[self.page_key], field_name=self.page_key)
        elems = _ensure_list(message.metadata[self.elems_key], field_name=self.elems_key)

        expected_sync_ids = max(self.page_size - 1, 0)
        raw_sync_ids: Missing[list[Any]]
        if self.sync_ids_key in message.metadata:
            raw_sync_ids = message.metadata[self.sync_ids_key]
        elif expected_sync_ids == 0:
            raw_sync_ids = []
        else:
            raise InvalidWidgetPayloadError(f"{self.sync_ids_key} is missing in metadata")

        raw_sync_ids_list = _ensure_list(raw_sync_ids, field_name=self.sync_ids_key)
        if len(raw_sync_ids_list) != expected_sync_ids:
            raise InvalidWidgetPayloadError("sync_ids length does not match page_size")

        sync_ids: list[UUID] = []
        for raw_id in raw_sync_ids_list:
            if isinstance(raw_id, UUID):
                sync_ids.append(raw_id)
                continue
            if isinstance(raw_id, str):
                try:
                    sync_ids.append(UUID(raw_id))
                except ValueError as exc:
                    raise InvalidWidgetPayloadError("sync_ids contains invalid UUID") from exc
                continue
            raise InvalidWidgetPayloadError("sync_ids contains invalid UUID")

        source_sync_id = _ensure_source_sync_id(message)

        items = self._page_items(elems, page)
        metadata = self._build_metadata(elems=elems, sync_ids=sync_ids, page=page)
        bubbles = self._build_page_bubbles(page=page, total_pages=self._total_pages(elems))

        edits: list[EditMessage] = []
        for idx, elem in enumerate(items):
            if idx < len(sync_ids):
                sync_id = sync_ids[idx]
            else:
                sync_id = source_sync_id
            edit_bubbles: Missing[BubbleMarkup] = Undefined
            if idx == len(items) - 1:
                edit_bubbles = bubbles
            edits.append(
                EditMessage(
                    bot_id=message.bot.id,
                    sync_id=sync_id,
                    body=self._render_body(elem),
                    metadata=metadata,
                    bubbles=edit_bubbles,
                )
            )

        return edits


@dataclass(slots=True)
class SingleWidgetState:
    elems: list[Any]
    current_index: int


@dataclass(slots=True)
class MultiWidgetState:
    elems: list[Any]
    page: int
    sync_ids: list[UUID]


WidgetState = SingleWidgetState | MultiWidgetState


__all__ = (
    "MultiMessageWidget",
    "SingleMessageWidget",
)
