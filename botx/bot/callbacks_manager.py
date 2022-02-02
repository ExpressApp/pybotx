import asyncio
from typing import TYPE_CHECKING, Dict, Optional
from uuid import UUID

from botx.bot.exceptions import BotShuttingDownError, BotXMethodCallbackNotFoundError
from botx.client.exceptions.callbacks import CallbackNotReceivedError
from botx.logger import logger
from botx.models.method_callbacks import BotXMethodCallback

if TYPE_CHECKING:
    from asyncio import Future  # noqa: WPS458


class CallbacksManager:
    def __init__(self) -> None:
        self._callback_futures: Dict[UUID, "Future[BotXMethodCallback]"] = {}

    def create_botx_method_callback(self, sync_id: UUID) -> None:
        self._callback_futures[sync_id] = asyncio.Future()

    def set_botx_method_callback_result(
        self,
        callback: BotXMethodCallback,
    ) -> None:
        sync_id = callback.sync_id
        future = self._pop_future(sync_id)

        if future.cancelled():
            logger.warning(
                f"BotX method with sync_id `{sync_id!s}` don't wait callback",
            )
            return

        future.set_result(callback)

    async def wait_botx_method_callback(
        self,
        sync_id: UUID,
        timeout: Optional[int],
    ) -> BotXMethodCallback:
        future = self._callback_futures[sync_id]

        try:
            return await asyncio.wait_for(future, timeout=timeout)
        except asyncio.TimeoutError as exc:
            raise CallbackNotReceivedError(sync_id) from exc

    def stop_callbacks_waiting(self) -> None:
        for sync_id, future in self._callback_futures.items():
            if not future.done():
                future.set_exception(
                    BotShuttingDownError(
                        f"Callback with sync_id `{sync_id!s}` can't be received",
                    ),
                )

    def _pop_future(self, sync_id: UUID) -> "Future[BotXMethodCallback]":
        try:
            future = self._callback_futures.pop(sync_id)
        except KeyError:
            raise BotXMethodCallbackNotFoundError(sync_id) from None

        return future
