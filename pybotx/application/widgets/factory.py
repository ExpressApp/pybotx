from __future__ import annotations

from typing import Any, Callable

from pybotx.domain.widgets import (
    DEFAULT_EMPTY_TEXT,
    DEFAULT_NEXT_LABEL,
    DEFAULT_PREV_LABEL,
    MultiMessageWidget,
    SingleMessageWidget,
)


class WidgetFactory:
    def __init__(self, *, include_state_in_metadata: bool = False) -> None:
        self._include_state_in_metadata = include_state_in_metadata

    def single(
        self,
        *,
        command: str,
        render_item: Callable[[Any], str] = str,
        prev_label: str = DEFAULT_PREV_LABEL,
        next_label: str = DEFAULT_NEXT_LABEL,
        elems_key: str = "elems",
        index_key: str = "current_index",
        include_state_in_metadata: bool | None = None,
    ) -> SingleMessageWidget:
        return SingleMessageWidget(
            command=command,
            render_item=render_item,
            prev_label=prev_label,
            next_label=next_label,
            elems_key=elems_key,
            index_key=index_key,
            include_state_in_metadata=(
                self._include_state_in_metadata
                if include_state_in_metadata is None
                else include_state_in_metadata
            ),
        )

    def multi(
        self,
        *,
        command: str,
        page_size: int,
        render_item: Callable[[Any], str] = str,
        prev_label: str = DEFAULT_PREV_LABEL,
        next_label: str = DEFAULT_NEXT_LABEL,
        empty_text: str = DEFAULT_EMPTY_TEXT,
        elems_key: str = "elems",
        sync_ids_key: str = "sync_ids",
        page_key: str = "page",
        include_state_in_metadata: bool | None = None,
    ) -> MultiMessageWidget:
        return MultiMessageWidget(
            command=command,
            page_size=page_size,
            render_item=render_item,
            prev_label=prev_label,
            next_label=next_label,
            empty_text=empty_text,
            elems_key=elems_key,
            sync_ids_key=sync_ids_key,
            page_key=page_key,
            include_state_in_metadata=(
                self._include_state_in_metadata
                if include_state_in_metadata is None
                else include_state_in_metadata
            ),
        )


__all__ = ("WidgetFactory",)
