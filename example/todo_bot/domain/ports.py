from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime
from typing import Protocol, runtime_checkable
from uuid import UUID

from example.todo_bot.domain.models import TodoItem


@runtime_checkable
class ClockPort(Protocol):
    def now(self) -> datetime: ...  # pragma: no cover


@runtime_checkable
class TodoRepositoryPort(Protocol):
    async def add(
        self,
        *,
        chat_id: UUID,
        text: str,
        created_at: datetime,
    ) -> TodoItem: ...  # pragma: no cover

    async def list(self, *, chat_id: UUID) -> Sequence[TodoItem]: ...  # pragma: no cover

    async def mark_done(
        self,
        *,
        chat_id: UUID,
        todo_id: int,
        completed_at: datetime,
    ) -> TodoItem: ...  # pragma: no cover

    async def delete(self, *, chat_id: UUID, todo_id: int) -> None: ...  # pragma: no cover

    async def clear(self, *, chat_id: UUID) -> int: ...  # pragma: no cover
