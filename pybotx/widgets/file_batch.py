from dataclasses import dataclass
from typing import Any

from pybotx.models.message.incoming_message import IncomingMessage

from .base import Widget

FILE_BATCH_FILES_KEY = "file_batch_files"
FILE_BATCH_PAGE_KEY = "file_batch_page"
FILE_BATCH_ACTION_KEY = "file_batch_action"
FILE_BATCH_FILE_NAME_KEY = "file_batch_file_name"

FILE_BATCH_ACTION_PREV = "prev"
FILE_BATCH_ACTION_NEXT = "next"
FILE_BATCH_ACTION_RETRY_FAILED = "retry_failed"
FILE_BATCH_ACTION_ITEM = "item"


@dataclass(frozen=True, slots=True)
class BatchFileItem:
    name: str
    status: str
    error: str = ""


def _safe_int(value: object) -> int:
    if isinstance(value, int):
        return value

    if isinstance(value, str) and value.isdigit():
        return int(value)

    return 0


def _normalize_item(raw_item: object) -> BatchFileItem | None:
    if isinstance(raw_item, BatchFileItem):
        return raw_item

    if isinstance(raw_item, dict):
        name = raw_item.get("name")
        status = raw_item.get("status")
        if name is None or status is None:
            return None

        return BatchFileItem(
            name=str(name),
            status=str(status),
            error=str(raw_item.get("error", "")),
        )

    if isinstance(raw_item, str):
        return BatchFileItem(name=raw_item, status="pending")

    return None


def _status_icon(status: str) -> str:
    if status in {"done", "ok", "success"}:
        return "✅"
    if status in {"failed", "error"}:
        return "❌"
    if status in {"running", "processing"}:
        return "⏳"
    return "•"


class FileBatchWidget(Widget):
    def __init__(
        self,
        files: list[BatchFileItem | dict[str, Any] | str] | None,
        label: str = "Пакет файлов",
        page_size: int = 5,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.label = label
        self.page_size = max(page_size, 1)

        raw_files = files
        if raw_files is None:
            metadata_files = self.message.metadata.get(FILE_BATCH_FILES_KEY, [])
            if isinstance(metadata_files, list):
                raw_files = metadata_files
            else:
                raw_files = []

        self.files = [item for raw_item in raw_files if (item := _normalize_item(raw_item))]
        self.page = _safe_int(
            self.message.data.get(
                FILE_BATCH_PAGE_KEY,
                self.message.metadata.get(FILE_BATCH_PAGE_KEY, 0),
            ),
        )
        self.page = min(max(self.page, 0), self._max_page())
        self.displayed_files = self._slice_files()

        self.widget_message.body = self._build_body()
        self._sync_metadata()

    def add_markup(self) -> None:
        for file_item in self.displayed_files:
            self.widget_bubbles.add_button(
                command=self.command,
                label=file_item.name,
                data={
                    FILE_BATCH_ACTION_KEY: FILE_BATCH_ACTION_ITEM,
                    FILE_BATCH_FILE_NAME_KEY: file_item.name,
                },
            )

        if self.page > 0:
            self.widget_bubbles.add_button(
                command=self.command,
                label="Назад",
                data={
                    FILE_BATCH_ACTION_KEY: FILE_BATCH_ACTION_PREV,
                    FILE_BATCH_PAGE_KEY: self.page - 1,
                },
            )

        if self.page < self._max_page():
            self.widget_bubbles.add_button(
                command=self.command,
                label="Вперед",
                data={
                    FILE_BATCH_ACTION_KEY: FILE_BATCH_ACTION_NEXT,
                    FILE_BATCH_PAGE_KEY: self.page + 1,
                },
                new_row=self.page == 0,
            )

        if self._failed_count() > 0:
            self.widget_bubbles.add_button(
                command=self.command,
                label="Повторить ошибки",
                data={FILE_BATCH_ACTION_KEY: FILE_BATCH_ACTION_RETRY_FAILED},
            )

        self.add_additional_markup()

    @classmethod
    def get_action(cls, message: IncomingMessage) -> str:
        action = message.data.get(FILE_BATCH_ACTION_KEY)
        if action not in {
            FILE_BATCH_ACTION_PREV,
            FILE_BATCH_ACTION_NEXT,
            FILE_BATCH_ACTION_RETRY_FAILED,
            FILE_BATCH_ACTION_ITEM,
        }:
            raise RuntimeError("File batch action is not found.")

        return str(action)

    @classmethod
    def get_selected_file(cls, message: IncomingMessage) -> str:
        file_name = message.data.get(FILE_BATCH_FILE_NAME_KEY)
        if file_name is None:
            raise RuntimeError("Selected file name is not found.")

        return str(file_name)

    def _max_page(self) -> int:
        if not self.files:
            return 0
        return (len(self.files) - 1) // self.page_size

    def _slice_files(self) -> list[BatchFileItem]:
        start = self.page * self.page_size
        end = start + self.page_size
        return self.files[start:end]

    def _failed_count(self) -> int:
        return sum(file_item.status in {"failed", "error"} for file_item in self.files)

    def _build_body(self) -> str:
        lines = [
            self.label,
            f"Всего: {len(self.files)}",
            f"Ошибок: {self._failed_count()}",
        ]
        for file_item in self.displayed_files:
            lines.append(f"{_status_icon(file_item.status)} {file_item.name}")
            if file_item.error:
                lines.append(f"  └ {file_item.error}")
        return "\n".join(lines)

    def _sync_metadata(self) -> None:
        self.widget_metadata[FILE_BATCH_FILES_KEY] = [
            {
                "name": file_item.name,
                "status": file_item.status,
                "error": file_item.error,
            }
            for file_item in self.files
        ]
        self.widget_metadata[FILE_BATCH_PAGE_KEY] = self.page
