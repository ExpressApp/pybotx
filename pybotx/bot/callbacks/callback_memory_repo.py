import asyncio
from typing import TYPE_CHECKING, Dict
from uuid import UUID

from pybotx.bot.callbacks.callback_repo_proto import CallbackRepoProto
from pybotx.bot.exceptions import BotShuttingDownError
from pybotx.client.exceptions.callbacks import CallbackNotReceivedError
from pybotx.logger import logger
from pybotx.models.method_callbacks import BotXMethodCallback

if TYPE_CHECKING:
    from asyncio import Future  # noqa: WPS458


class CallbackMemoryRepo(CallbackRepoProto):
    def __init__(self, timeout: float = 0) -> None:
        self._callback_futures: Dict[UUID, "Future[BotXMethodCallback]"] = {}
        self.timeout = timeout

    async def create_botx_method_callback(self, sync_id: UUID) -> None:
        self._callback_futures.setdefault(sync_id, asyncio.Future())

    async def set_botx_method_callback_result(
        self,
        callback: BotXMethodCallback,
    ) -> None:
        sync_id = callback.sync_id

        if sync_id not in self._callback_futures:
            logger.warning(
                f"Callback `{sync_id}` doesn't exist yet or already "
                f"waited or timed out. Waiting for {self.timeout}s "
                f"for it or will be ignored.",
            )
            self._callback_futures.setdefault(sync_id, asyncio.Future())
            asyncio.create_task(self._wait_and_drop_orphan_callback(sync_id))

        future = self._callback_futures[sync_id]
        future.set_result(callback)

    async def wait_botx_method_callback(
        self,
        sync_id: UUID,
        timeout: float,
    ) -> BotXMethodCallback:
        future = self._callback_futures[sync_id]

        try:
            result = await asyncio.wait_for(future, timeout=timeout)
        except asyncio.TimeoutError as exc:
            del self._callback_futures[sync_id]  # noqa: WPS420
            raise CallbackNotReceivedError(sync_id) from exc

        del self._callback_futures[sync_id]  # noqa: WPS420
        return result

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

    async def _wait_and_drop_orphan_callback(self, sync_id: UUID) -> None:
        await asyncio.sleep(self.timeout)
        if sync_id not in self._callback_futures:
            return

        self._callback_futures.pop(sync_id, None)
        logger.debug(f"Callback `{sync_id}` was dropped")
