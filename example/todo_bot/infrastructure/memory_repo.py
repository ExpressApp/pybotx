from __future__ import annotations

import asyncio
from collections.abc import Sequence
from datetime import datetime
from uuid import UUID

from example.todo_bot.domain.errors import TodoNotFoundError
from example.todo_bot.domain.models import TodoItem
from example.todo_bot.domain.ports import TodoRepositoryPort


class InMemoryTodoRepository(TodoRepositoryPort):
    def __init__(self) -> None:
        self._items: dict[UUID, list[TodoItem]] = {}
        self._next_id: dict[UUID, int] = {}
        self._lock = asyncio.Lock()

    async def add(
        self,
        *,
        chat_id: UUID,
        text: str,
        created_at: datetime,
    ) -> TodoItem:
        async with self._lock:
            next_id = self._next_id.get(chat_id, 1)
            item = TodoItem(
                id=next_id,
                chat_id=chat_id,
                text=text,
                created_at=created_at,
            )
            self._next_id[chat_id] = next_id + 1
            self._items.setdefault(chat_id, []).append(item)
            return item

    async def list(self, *, chat_id: UUID) -> Sequence[TodoItem]:
        async with self._lock:
            return list(self._items.get(chat_id, []))

    async def mark_done(
        self,
        *,
        chat_id: UUID,
        todo_id: int,
        completed_at: datetime,
    ) -> TodoItem:
        async with self._lock:
            items = self._items.get(chat_id, [])
            for item in items:
                if item.id == todo_id:
                    item.completed_at = completed_at
                    return item
        raise TodoNotFoundError(chat_id, todo_id)

    async def delete(self, *, chat_id: UUID, todo_id: int) -> None:
        async with self._lock:
            items = self._items.get(chat_id, [])
            for index, item in enumerate(items):
                if item.id == todo_id:
                    del items[index]
                    return
        raise TodoNotFoundError(chat_id, todo_id)

    async def clear(self, *, chat_id: UUID) -> int:
        async with self._lock:
            items = self._items.pop(chat_id, [])
            return len(items)
