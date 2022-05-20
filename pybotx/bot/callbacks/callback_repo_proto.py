from typing import TYPE_CHECKING
from uuid import UUID

from pybotx.models.method_callbacks import BotXMethodCallback

if TYPE_CHECKING:
    from asyncio import Future  # noqa: WPS458

try:
    from typing import Protocol
except ImportError:
    from typing_extensions import Protocol  # type: ignore  # noqa: WPS440


class CallbackRepoProto(Protocol):
    async def create_botx_method_callback(self, sync_id: UUID) -> None:
        ...  # noqa: WPS428

    async def set_botx_method_callback_result(
        self,
        callback: BotXMethodCallback,
    ) -> None:
        ...  # noqa: WPS428

    async def wait_botx_method_callback(
        self,
        sync_id: UUID,
        timeout: float,
    ) -> BotXMethodCallback:
        ...  # noqa: WPS428

    async def pop_botx_method_callback(
        self,
        sync_id: UUID,
    ) -> "Future[BotXMethodCallback]":
        ...  # noqa: WPS428

    async def stop_callbacks_waiting(self) -> None:
        ...  # noqa: WPS428
