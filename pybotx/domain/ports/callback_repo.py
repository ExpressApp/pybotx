from typing import TYPE_CHECKING
from uuid import UUID

from pybotx.domain.models.method_callbacks import BotXMethodCallback

if TYPE_CHECKING:
    from asyncio import Future

from typing import Protocol, runtime_checkable


@runtime_checkable
class CallbackRepoProto(Protocol):
    async def create_botx_method_callback(
        self,
        sync_id: UUID,
    ) -> None: ...  # pragma: no cover

    async def set_botx_method_callback_result(
        self,
        callback: BotXMethodCallback,
    ) -> None: ...  # pragma: no cover

    async def wait_botx_method_callback(
        self,
        sync_id: UUID,
        timeout: float,
    ) -> BotXMethodCallback: ...  # pragma: no cover

    async def pop_botx_method_callback(
        self,
        sync_id: UUID,
    ) -> "Future[BotXMethodCallback]": ...  # pragma: no cover

    async def stop_callbacks_waiting(self) -> None: ...  # pragma: no cover
