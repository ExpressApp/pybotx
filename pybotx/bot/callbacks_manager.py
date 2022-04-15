import asyncio
from typing import TYPE_CHECKING, Dict, Literal, Optional, overload
from uuid import UUID

from pybotx.bot.exceptions import BotShuttingDownError, BotXMethodCallbackNotFoundError
from pybotx.client.exceptions.callbacks import CallbackNotReceivedError
from pybotx.logger import logger
from pybotx.models.method_callbacks import BotXMethodCallback

if TYPE_CHECKING:
    from asyncio import Future  # noqa: WPS458


def callback_timeout_alarm(
    callbacks_manager: "CallbacksManager",
    sync_id: UUID,
) -> None:
    callbacks_manager.cancel_callback_timeout_alarm(sync_id)
    future = callbacks_manager.pop_botx_method_callback(sync_id)

    if future.done():
        logger.warning(
            "Callback `{sync_id}` wasn't waited, but it was received:\n{result}",
            sync_id=sync_id,
            result=future.result(),
        )
    else:
        logger.error("Callback `{sync_id}` wasn't waited, also it wasn't received")


class CallbacksManager:
    def __init__(self) -> None:
        self._callback_futures: Dict[UUID, "Future[BotXMethodCallback]"] = {}
        self._callback_alarms: Dict[UUID, asyncio.TimerHandle] = {}

    def create_botx_method_callback(self, sync_id: UUID) -> None:
        self._callback_futures[sync_id] = asyncio.Future()

    def get_botx_method_callback(self, sync_id: UUID) -> "Future[BotXMethodCallback]":
        try:
            return self._callback_futures[sync_id]
        except KeyError:
            raise BotXMethodCallbackNotFoundError(sync_id) from None

    def set_botx_method_callback_result(
        self,
        callback: BotXMethodCallback,
    ) -> None:
        sync_id = callback.sync_id

        future = self.get_botx_method_callback(sync_id)
        if future.cancelled():
            logger.warning(
                f"BotX method with sync_id `{sync_id!s}` don't wait callback",
            )
            return

        future.set_result(callback)

    async def wait_botx_method_callback(
        self,
        sync_id: UUID,
        timeout: float,
    ) -> BotXMethodCallback:
        future = self.get_botx_method_callback(sync_id)

        try:
            return await asyncio.wait_for(future, timeout=timeout)
        except asyncio.TimeoutError as exc:
            raise CallbackNotReceivedError(sync_id) from exc

    def pop_botx_method_callback(self, sync_id: UUID) -> "Future[BotXMethodCallback]":
        return self._callback_futures.pop(sync_id)

    def stop_callbacks_waiting(self) -> None:
        for sync_id, future in self._callback_futures.items():
            if not future.done():
                future.set_exception(
                    BotShuttingDownError(
                        f"Callback with sync_id `{sync_id!s}` can't be received",
                    ),
                )

    def setup_callback_timeout_alarm(self, sync_id: UUID, timeout: float) -> None:
        loop = asyncio.get_event_loop()

        self._callback_alarms[sync_id] = loop.call_later(
            timeout,
            callback_timeout_alarm,
            self,
            sync_id,
        )

    @overload
    def cancel_callback_timeout_alarm(
        self,
        sync_id: UUID,
    ) -> None:
        ...  # noqa: WPS428

    @overload
    def cancel_callback_timeout_alarm(
        self,
        sync_id: UUID,
        return_remaining_time: Literal[True],
    ) -> float:
        ...  # noqa: WPS428

    def cancel_callback_timeout_alarm(
        self,
        sync_id: UUID,
        return_remaining_time: bool = False,
    ) -> Optional[float]:
        try:
            alarm = self._callback_alarms.pop(sync_id)
        except KeyError:
            raise ValueError(
                f"Callback `{sync_id}` doesn't exist or already waited or timed out",
            ) from None

        time_before_alarm: Optional[float] = None

        if return_remaining_time:
            loop = asyncio.get_event_loop()
            time_before_alarm = alarm.when() - loop.time()

        alarm.cancel()

        return time_before_alarm
