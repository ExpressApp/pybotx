from __future__ import annotations

import asyncio
from typing import Any
from uuid import UUID

from pybotx.domain.errors import InvalidWidgetPayloadError
from pybotx.domain.missing import Missing, Undefined
from pybotx.domain.models.message.edit_message import EditMessage
from pybotx.domain.models.message.incoming_message import IncomingMessage
from pybotx.domain.models.message.markup import BubbleMarkup
from pybotx.domain.models.message.outgoing_message import OutgoingMessage
from pybotx.domain.ports.widget_state_store import WidgetStateStorePort
from pybotx.domain.widgets import (
    MultiMessageWidget,
    MultiWidgetState,
    SingleMessageWidget,
    SingleWidgetState,
    WidgetState,
)


class WidgetSession:
    def __init__(
        self,
        *,
        widget: SingleMessageWidget | MultiMessageWidget,
        store: WidgetStateStorePort,
        ttl_seconds: float | None = None,
        include_metadata: bool = False,
    ) -> None:
        self._widget = widget
        self._store = store
        self._ttl_seconds = ttl_seconds
        self._include_metadata = include_metadata

    @staticmethod
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

    async def send_single(
        self,
        *,
        bot,
        bot_id: UUID,
        chat_id: UUID,
        elems: list[Any],
        current_index: int = 0,
        wait_callback: bool = True,
        callback_timeout: float | None = None,
    ) -> UUID:
        if not isinstance(self._widget, SingleMessageWidget):
            raise InvalidWidgetPayloadError("WidgetSession is not configured for single widgets")

        body, metadata, bubbles = self._widget.render(
            elems=elems,
            current_index=current_index,
        )
        if not self._include_metadata:
            metadata = {}

        message = OutgoingMessage(
            bot_id=bot_id,
            chat_id=chat_id,
            body=body,
            metadata=metadata,
            bubbles=bubbles,
        )

        sync_id = await bot.send(
            message=message,
            wait_callback=wait_callback,
            callback_timeout=callback_timeout,
        )

        await self._store.set(
            sync_id,
            SingleWidgetState(elems=list(elems), current_index=current_index),
            ttl_seconds=self._ttl_seconds,
        )

        return sync_id

    async def send_multi(
        self,
        *,
        bot,
        bot_id: UUID,
        chat_id: UUID,
        elems: list[Any],
        page: int = 0,
        wait_callback: bool = True,
        callback_timeout: float | None = None,
    ) -> tuple[list[UUID], UUID]:
        if not isinstance(self._widget, MultiMessageWidget):
            raise InvalidWidgetPayloadError("WidgetSession is not configured for multi widgets")

        head_messages = self._widget.build_outgoing_head_messages(
            bot_id=bot_id,
            chat_id=chat_id,
            elems=elems,
            page=page,
        )
        head_sync_ids: list[UUID] = []
        for message in head_messages:
            sync_id = await bot.send(
                message=message,
                wait_callback=wait_callback,
                callback_timeout=callback_timeout,
            )
            head_sync_ids.append(sync_id)

        tail_message = self._widget.build_outgoing_tail_message(
            bot_id=bot_id,
            chat_id=chat_id,
            elems=elems,
            page=page,
            sync_ids=head_sync_ids,
        )
        if not self._include_metadata:
            tail_message = OutgoingMessage(
                bot_id=tail_message.bot_id,
                chat_id=tail_message.chat_id,
                body=tail_message.body,
                metadata={},
                bubbles=tail_message.bubbles,
            )

        tail_sync_id = await bot.send(
            message=tail_message,
            wait_callback=wait_callback,
            callback_timeout=callback_timeout,
        )

        await self._store.set(
            tail_sync_id,
            MultiWidgetState(elems=list(elems), page=page, sync_ids=head_sync_ids),
            ttl_seconds=self._ttl_seconds,
        )

        return head_sync_ids, tail_sync_id

    async def update(
        self,
        *,
        bot,
        message: IncomingMessage,
        diff: bool = True,
        max_concurrency: int | None = None,
    ) -> list[UUID]:
        if message.source_sync_id is None:
            raise InvalidWidgetPayloadError("Widget command has no source_sync_id")

        state = await self._store.get(message.source_sync_id)
        if state is None:
            raise InvalidWidgetPayloadError("Widget state not found")

        if isinstance(self._widget, SingleMessageWidget):
            if not isinstance(state, SingleWidgetState):
                raise InvalidWidgetPayloadError("Widget state type mismatch")
            return await self._update_single(
                bot=bot,
                message=message,
                state=state,
                diff=diff,
            )
        if isinstance(self._widget, MultiMessageWidget):
            if not isinstance(state, MultiWidgetState):
                raise InvalidWidgetPayloadError("Widget state type mismatch")
            return await self._update_multi(
                bot=bot,
                message=message,
                state=state,
                diff=diff,
                max_concurrency=max_concurrency,
            )

        raise InvalidWidgetPayloadError("Unsupported widget type")

    async def _update_single(
        self,
        *,
        bot,
        message: IncomingMessage,
        state: SingleWidgetState,
        diff: bool,
    ) -> list[UUID]:
        if self._widget.index_key not in message.data:
            raise InvalidWidgetPayloadError(f"{self._widget.index_key} is missing in data")

        target_index = self._parse_int(
            message.data[self._widget.index_key],
            field_name=self._widget.index_key,
        )
        if diff and target_index == state.current_index:
            return []

        body, metadata, bubbles = self._widget.render(
            elems=state.elems,
            current_index=target_index,
        )
        if not self._include_metadata:
            metadata = {}

        edit = EditMessage(
            bot_id=message.bot.id,
            sync_id=message.source_sync_id,
            body=body,
            metadata=metadata,
            bubbles=bubbles,
        )
        await bot.edit(message=edit)

        state.current_index = target_index
        await self._store.set(
            message.source_sync_id,
            state,
            ttl_seconds=self._ttl_seconds,
        )

        return [edit.sync_id]

    async def _update_multi(
        self,
        *,
        bot,
        message: IncomingMessage,
        state: MultiWidgetState,
        diff: bool,
        max_concurrency: int | None,
    ) -> list[UUID]:
        if self._widget.page_key not in message.data:
            raise InvalidWidgetPayloadError(f"{self._widget.page_key} is missing in data")

        target_page = self._parse_int(
            message.data[self._widget.page_key],
            field_name=self._widget.page_key,
        )
        if diff and target_page == state.page:
            return []

        items = self._widget._page_items(state.elems, target_page)
        bubbles = self._widget._build_page_bubbles(
            page=target_page,
            total_pages=self._widget._total_pages(state.elems),
        )
        metadata: dict[str, Any] | Missing[dict[str, Any]] = {}
        if self._include_metadata:
            metadata = self._widget._build_metadata(
                elems=state.elems,
                sync_ids=state.sync_ids,
                page=target_page,
            )

        edits: list[EditMessage] = []
        for idx, elem in enumerate(items):
            if idx < len(state.sync_ids):
                sync_id = state.sync_ids[idx]
            else:
                sync_id = message.source_sync_id
            edit_bubbles: Missing[BubbleMarkup] = Undefined
            if idx == len(items) - 1:
                edit_bubbles = bubbles
            edits.append(
                EditMessage(
                    bot_id=message.bot.id,
                    sync_id=sync_id,
                    body=self._widget._render_body(elem),
                    metadata=metadata,
                    bubbles=edit_bubbles,
                )
            )

        await self._apply_edits(bot=bot, edits=edits, max_concurrency=max_concurrency)

        state.page = target_page
        await self._store.set(
            message.source_sync_id,
            state,
            ttl_seconds=self._ttl_seconds,
        )

        return [edit.sync_id for edit in edits]

    @staticmethod
    async def _apply_edits(
        *,
        bot,
        edits: list[EditMessage],
        max_concurrency: int | None,
    ) -> None:
        if not edits:
            return

        if max_concurrency is None or max_concurrency <= 1:
            for edit in edits:
                await bot.edit(message=edit)
            return

        semaphore = asyncio.Semaphore(max_concurrency)

        async def _run(edit: EditMessage) -> None:
            async with semaphore:
                await bot.edit(message=edit)

        await asyncio.gather(*(_run(edit) for edit in edits))


__all__ = ("WidgetSession", "SingleWidgetState", "MultiWidgetState", "WidgetState")
