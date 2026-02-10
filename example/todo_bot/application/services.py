from __future__ import annotations

from collections.abc import Sequence
from uuid import UUID

from example.todo_bot.domain.errors import TodoValidationError
from example.todo_bot.domain.models import TodoItem
from example.todo_bot.domain.ports import ClockPort, TodoRepositoryPort


class TodoService:
    def __init__(
        self,
        *,
        repo: TodoRepositoryPort,
        clock: ClockPort,
        max_text_length: int = 500,
    ) -> None:
        self._repo = repo
        self._clock = clock
        self._max_text_length = max_text_length

    async def add(self, *, chat_id: UUID, text: str) -> TodoItem:
        cleaned = text.strip()
        if not cleaned:
            raise TodoValidationError("Todo text is required.")
        if len(cleaned) > self._max_text_length:
            raise TodoValidationError("Todo text is too long.")

        return await self._repo.add(
            chat_id=chat_id,
            text=cleaned,
            created_at=self._clock.now(),
        )

    async def list(self, *, chat_id: UUID) -> Sequence[TodoItem]:
        return await self._repo.list(chat_id=chat_id)

    async def mark_done(self, *, chat_id: UUID, todo_id: int) -> TodoItem:
        return await self._repo.mark_done(
            chat_id=chat_id,
            todo_id=todo_id,
            completed_at=self._clock.now(),
        )

    async def delete(self, *, chat_id: UUID, todo_id: int) -> None:
        await self._repo.delete(chat_id=chat_id, todo_id=todo_id)

    async def clear(self, *, chat_id: UUID) -> int:
        return await self._repo.clear(chat_id=chat_id)
