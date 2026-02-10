from __future__ import annotations

import asyncio
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from typing import Any
from uuid import UUID

from pybotx.application.widgets.session import WidgetSession
from pybotx.domain.models.message.incoming_message import IncomingMessage
from pybotx.domain.ports.widget_state_store import WidgetStateStorePort
from pybotx.domain.widgets import MultiMessageWidget, SingleMessageWidget


@dataclass(slots=True)
class MultiWidgetSendResult:
    head_sync_ids: list[UUID]
    tail_sync_id: UUID


class BotWidgetsMixin:
    @staticmethod
    def _parse_optional_int(value: Any | None) -> int | None:
        if value is None:
            return None
        if isinstance(value, bool):
            return None
        if isinstance(value, int):
            return value
        if isinstance(value, str):
            try:
                return int(value)
            except ValueError:
                return None
        return None

    async def _apply_edits(
        self,
        *,
        edits: Iterable[Any],
        max_concurrency: int | None,
    ) -> None:
        edit_list = list(edits)
        if not edit_list:
            return

        if max_concurrency is None or max_concurrency <= 1:
            for edit in edit_list:
                await self.edit(message=edit)
            return

        semaphore = asyncio.Semaphore(max_concurrency)

        async def _run(edit: Any) -> None:
            async with semaphore:
                await self.edit(message=edit)

        await asyncio.gather(*(_run(edit) for edit in edit_list))

    async def send_single_widget(
        self,
        *,
        bot_id: UUID,
        chat_id: UUID,
        widget: SingleMessageWidget,
        elems: Sequence[Any],
        current_index: int = 0,
        wait_callback: bool = True,
        callback_timeout: float | None = None,
    ) -> UUID:
        message = widget.build_outgoing(
            bot_id=bot_id,
            chat_id=chat_id,
            elems=elems,
            current_index=current_index,
        )
        return await self.send(
            message=message,
            wait_callback=wait_callback,
            callback_timeout=callback_timeout,
        )

    async def send_multi_widget(
        self,
        *,
        bot_id: UUID,
        chat_id: UUID,
        widget: MultiMessageWidget,
        elems: Sequence[Any],
        page: int = 0,
        wait_callback: bool = True,
        callback_timeout: float | None = None,
    ) -> MultiWidgetSendResult:
        head_messages = widget.build_outgoing_head_messages(
            bot_id=bot_id,
            chat_id=chat_id,
            elems=elems,
            page=page,
        )
        head_sync_ids: list[UUID] = []
        for message in head_messages:
            sync_id = await self.send(
                message=message,
                wait_callback=wait_callback,
                callback_timeout=callback_timeout,
            )
            head_sync_ids.append(sync_id)

        tail_message = widget.build_outgoing_tail_message(
            bot_id=bot_id,
            chat_id=chat_id,
            elems=elems,
            page=page,
            sync_ids=head_sync_ids,
        )
        tail_sync_id = await self.send(
            message=tail_message,
            wait_callback=wait_callback,
            callback_timeout=callback_timeout,
        )

        return MultiWidgetSendResult(
            head_sync_ids=head_sync_ids,
            tail_sync_id=tail_sync_id,
        )

    async def update_widget(
        self,
        *,
        widget: SingleMessageWidget | MultiMessageWidget,
        message: IncomingMessage,
        max_concurrency: int | None = None,
        diff: bool = True,
    ) -> list[UUID]:
        if isinstance(widget, SingleMessageWidget):
            current_index = self._parse_optional_int(
                message.metadata.get(widget.index_key),
            )
            target_index = self._parse_optional_int(
                message.data.get(widget.index_key),
            )
            if diff and current_index is not None and target_index is not None:
                if current_index == target_index:
                    return []

            edit = widget.build_edit_from_message(message)
            await self.edit(message=edit)
            return [edit.sync_id]
        if isinstance(widget, MultiMessageWidget):
            current_page = self._parse_optional_int(
                message.metadata.get(widget.page_key),
            )
            target_page = self._parse_optional_int(
                message.data.get(widget.page_key),
            )
            if diff and current_page is not None and target_page is not None:
                if current_page == target_page:
                    return []

            edits = widget.build_edit_from_message(message)
            await self._apply_edits(edits=edits, max_concurrency=max_concurrency)
            return [edit.sync_id for edit in edits]

        raise TypeError("Unsupported widget type")

    def widget_session(
        self,
        *,
        widget: SingleMessageWidget | MultiMessageWidget,
        store: WidgetStateStorePort | None = None,
        ttl_seconds: float | None = None,
        include_metadata: bool = False,
    ) -> WidgetSession:
        if store is None:
            store = getattr(self, "_widget_state_store", None)
        if store is None:
            raise ValueError("Widget state store is not configured")
        return WidgetSession(
            widget=widget,
            store=store,
            ttl_seconds=ttl_seconds,
            include_metadata=include_metadata,
        )


__all__ = ("BotWidgetsMixin", "MultiWidgetSendResult")
