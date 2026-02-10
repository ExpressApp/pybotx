from __future__ import annotations

from typing import Protocol, runtime_checkable
from uuid import UUID

from pybotx.domain.models.method_callbacks import BotXMethodCallback


@runtime_checkable
class CallbackManagerPort(Protocol):
    def register_expected_callback(self, sync_id: UUID) -> None: ...  # pragma: no cover

    async def create_botx_method_callback(self, sync_id: UUID) -> None: ...  # pragma: no cover

    async def set_botx_method_callback_result(
        self,
        callback: BotXMethodCallback,
    ) -> None: ...  # pragma: no cover

    async def wait_botx_method_callback(
        self,
        sync_id: UUID,
        timeout: float,
    ) -> BotXMethodCallback: ...  # pragma: no cover

    async def stop_callbacks_waiting(self) -> None: ...  # pragma: no cover

    def setup_callback_timeout_alarm(self, sync_id: UUID, timeout: float) -> None: ...  # pragma: no cover

    def cancel_callback_timeout_alarm(
        self,
        sync_id: UUID,
        return_remaining_time: bool = False,
    ) -> float | None: ...  # pragma: no cover
