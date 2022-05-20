import asyncio
from typing import Dict, Literal, NamedTuple, Optional, overload
from uuid import UUID

from pybotx.bot.callbacks.callback_repo_proto import CallbackRepoProto
from pybotx.bot.exceptions import BotXMethodCallbackNotFoundError
from pybotx.logger import logger
from pybotx.models.method_callbacks import BotXMethodCallback


class CallbackAlarm(NamedTuple):
    alarm_time: float
    # TODO: Fix after dropping Python 3.8
    task: asyncio.Future  # type: ignore


async def _callback_timeout_alarm(
    callbacks_manager: "CallbackManager",
    sync_id: UUID,
    timeout: float,
) -> None:
    await asyncio.sleep(timeout)

    callbacks_manager.cancel_callback_timeout_alarm(sync_id)
    await callbacks_manager.pop_botx_method_callback(sync_id)

    logger.error("Callback `{sync_id}` wasn't waited", sync_id=sync_id)


class CallbackManager:
    def __init__(self, callback_repo: CallbackRepoProto) -> None:
        self._callback_repo = callback_repo
        self._callback_alarms: Dict[UUID, CallbackAlarm] = {}

    async def create_botx_method_callback(self, sync_id: UUID) -> None:
        await self._callback_repo.create_botx_method_callback(sync_id)

    async def set_botx_method_callback_result(
        self,
        callback: BotXMethodCallback,
    ) -> None:
        await self._callback_repo.set_botx_method_callback_result(callback)

    async def wait_botx_method_callback(
        self,
        sync_id: UUID,
        timeout: float,
    ) -> BotXMethodCallback:
        return await self._callback_repo.wait_botx_method_callback(sync_id, timeout)

    async def pop_botx_method_callback(
        self,
        sync_id: UUID,
    ) -> "asyncio.Future[BotXMethodCallback]":
        return await self._callback_repo.pop_botx_method_callback(sync_id)

    async def stop_callbacks_waiting(self) -> None:
        await self._callback_repo.stop_callbacks_waiting()

    def setup_callback_timeout_alarm(self, sync_id: UUID, timeout: float) -> None:
        loop = asyncio.get_event_loop()

        self._callback_alarms[sync_id] = CallbackAlarm(
            alarm_time=loop.time() + timeout,
            task=asyncio.create_task(_callback_timeout_alarm(self, sync_id, timeout)),
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
            alarm_time, alarm = self._callback_alarms.pop(sync_id)
        except KeyError:
            raise BotXMethodCallbackNotFoundError(sync_id) from None

        time_before_alarm: Optional[float] = None

        if return_remaining_time:
            loop = asyncio.get_event_loop()
            time_before_alarm = alarm_time - loop.time()

        alarm.cancel()

        return time_before_alarm
