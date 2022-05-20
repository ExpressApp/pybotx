import asyncio
from typing import TYPE_CHECKING, Dict
from uuid import UUID

from pybotx.bot.callbacks.callback_repo_proto import CallbackRepoProto
from pybotx.bot.exceptions import BotShuttingDownError, BotXMethodCallbackNotFoundError
from pybotx.client.exceptions.callbacks import CallbackNotReceivedError
from pybotx.models.method_callbacks import BotXMethodCallback

if TYPE_CHECKING:
    from asyncio import Future  # noqa: WPS458


class CallbackMemoryRepo(CallbackRepoProto):
    def __init__(self) -> None:
        self._callback_futures: Dict[UUID, "Future[BotXMethodCallback]"] = {}

    async def create_botx_method_callback(self, sync_id: UUID) -> None:
        self._callback_futures[sync_id] = asyncio.Future()

    async def set_botx_method_callback_result(
        self,
        callback: BotXMethodCallback,
    ) -> None:
        sync_id = callback.sync_id

        future = self._get_botx_method_callback(sync_id)
        future.set_result(callback)

    async def wait_botx_method_callback(
        self,
        sync_id: UUID,
        timeout: float,
    ) -> BotXMethodCallback:
        future = self._get_botx_method_callback(sync_id)

        try:
            return await asyncio.wait_for(future, timeout=timeout)
        except asyncio.TimeoutError as exc:
            del self._callback_futures[sync_id]  # noqa: WPS420
            raise CallbackNotReceivedError(sync_id) from exc

    async def pop_botx_method_callback(
        self,
        sync_id: UUID,
    ) -> "Future[BotXMethodCallback]":
        return self._callback_futures.pop(sync_id)

    async def stop_callbacks_waiting(self) -> None:
        for sync_id, future in self._callback_futures.items():
            if not future.done():
                future.set_exception(
                    BotShuttingDownError(
                        f"Callback with sync_id `{sync_id!s}` can't be received",
                    ),
                )

    def _get_botx_method_callback(self, sync_id: UUID) -> "Future[BotXMethodCallback]":
        try:
            return self._callback_futures[sync_id]
        except KeyError:
            raise BotXMethodCallbackNotFoundError(sync_id) from None
