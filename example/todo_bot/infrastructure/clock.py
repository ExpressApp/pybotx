from __future__ import annotations

from datetime import datetime, timezone

from example.todo_bot.domain.ports import ClockPort


class SystemClock(ClockPort):
    def now(self) -> datetime:
        return datetime.now(tz=timezone.utc)
