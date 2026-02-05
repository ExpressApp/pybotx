from typing import TYPE_CHECKING
from uuid import UUID

from pybotx.models.method_callbacks import BotXMethodCallback

if TYPE_CHECKING:
    from asyncio import Future

try:
    from typing import Protocol
except ImportError:
    from typing_extensions import Protocol


class CallbackRepoProto(Protocol):
    async def create_botx_method_callback(
        self,
        sync_id: UUID,
    ) -> None: ...

    async def set_botx_method_callback_result(
        self,
        callback: BotXMethodCallback,
    ) -> None: ...

    async def wait_botx_method_callback(
        self,
        sync_id: UUID,
        timeout: float,
    ) -> BotXMethodCallback: ...

    async def pop_botx_method_callback(
        self,
        sync_id: UUID,
    ) -> "Future[BotXMethodCallback]": ...

    async def stop_callbacks_waiting(self) -> None: ...
