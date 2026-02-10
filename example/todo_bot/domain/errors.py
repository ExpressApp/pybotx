from __future__ import annotations

from uuid import UUID


class TodoValidationError(Exception):
    """Invalid input for todo operations."""


class TodoNotFoundError(Exception):
    def __init__(self, chat_id: UUID, todo_id: int) -> None:
        self.chat_id = chat_id
        self.todo_id = todo_id
        super().__init__(f"Todo `{todo_id}` not found in chat `{chat_id}`")
