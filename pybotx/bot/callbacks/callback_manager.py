import asyncio
from typing import Dict, Literal, NamedTuple, Optional, Set, overload
from uuid import UUID

from pybotx.bot.callbacks.callback_repo_proto import CallbackRepoProto
from pybotx.bot.exceptions import BotXMethodCallbackNotFoundError
from pybotx.client.exceptions.callbacks import CallbackNotReceivedError
from pybotx.logger import logger
from pybotx.models.method_callbacks import BotXMethodCallback

ORPHAN_CALLBACK_TTL_SECONDS = 5.0
ORPHAN_PENDING_CALLBACKS_LIMIT = 1000


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


async def _orphan_callback_alarm(
    callbacks_manager: "CallbackManager",
    sync_id: UUID,
    timeout: float,
) -> None:
    await asyncio.sleep(timeout)

    callbacks_manager.cancel_orphan_callback_alarm(sync_id)
    callbacks_manager.drop_orphan_callback(sync_id)

    logger.warning(
        "Callback `{sync_id}` received without a registered handler and expired",
        sync_id=sync_id,
    )


class CallbackManager:
    def __init__(self, callback_repo: CallbackRepoProto) -> None:
        self._callback_repo = callback_repo
        self._callback_alarms: Dict[UUID, CallbackAlarm] = {}
        self._orphan_callback_alarms: Dict[UUID, CallbackAlarm] = {}
        self._expected_sync_ids: Set[UUID] = set()
        self._pending_callbacks: Dict[UUID, BotXMethodCallback] = {}
        self._expired_sync_ids: Set[UUID] = set()

    def register_expected_callback(self, sync_id: UUID) -> None:
        self._expected_sync_ids.add(sync_id)
        self.cancel_orphan_callback_alarm(sync_id)

    async def create_botx_method_callback(self, sync_id: UUID) -> None:
        await self._callback_repo.create_botx_method_callback(sync_id)
        pending = self._pending_callbacks.pop(sync_id, None)
        if pending is not None:
            await self._callback_repo.set_botx_method_callback_result(pending)
            self.cancel_orphan_callback_alarm(sync_id)
        self._expected_sync_ids.discard(sync_id)

    async def set_botx_method_callback_result(
        self,
        callback: BotXMethodCallback,
    ) -> None:
        sync_id = callback.sync_id
        if sync_id in self._expired_sync_ids:
            raise BotXMethodCallbackNotFoundError(sync_id) from None
        try:
            await self._callback_repo.set_botx_method_callback_result(callback)
        except BotXMethodCallbackNotFoundError:
            if sync_id in self._pending_callbacks:
                self._pending_callbacks[sync_id] = callback
                return
            if sync_id in self._expected_sync_ids:
                self._pending_callbacks[sync_id] = callback
                return
            if len(self._orphan_callback_alarms) >= ORPHAN_PENDING_CALLBACKS_LIMIT:
                logger.warning(
                    "Pending callbacks limit reached; dropping orphan callback "
                    "`{sync_id}`",
                    sync_id=sync_id,
                )
                return
            self._pending_callbacks[sync_id] = callback
            self._setup_orphan_callback_alarm(sync_id, ORPHAN_CALLBACK_TTL_SECONDS)
            logger.warning(
                "Callback `{sync_id}` received without a registered handler; "
                "buffering",
                sync_id=sync_id,
            )
            return

    async def wait_botx_method_callback(
        self,
        sync_id: UUID,
        timeout: float,
    ) -> BotXMethodCallback:
        try:
            return await self._callback_repo.wait_botx_method_callback(
                sync_id, timeout
            )
        except CallbackNotReceivedError:
            self._mark_callback_expired(sync_id)
            raise

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
    ) -> None: ...  # noqa: WPS428, E704

    @overload
    def cancel_callback_timeout_alarm(
        self,
        sync_id: UUID,
        return_remaining_time: Literal[True],
    ) -> float: ...  # noqa: WPS428, E704

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

    def _setup_orphan_callback_alarm(self, sync_id: UUID, timeout: float) -> None:
        if sync_id in self._orphan_callback_alarms:
            return
        loop = asyncio.get_event_loop()
        self._orphan_callback_alarms[sync_id] = CallbackAlarm(
            alarm_time=loop.time() + timeout,
            task=asyncio.create_task(_orphan_callback_alarm(self, sync_id, timeout)),
        )

    def cancel_orphan_callback_alarm(self, sync_id: UUID) -> None:
        alarm = self._orphan_callback_alarms.pop(sync_id, None)
        if alarm is None:
            return
        alarm.task.cancel()

    def mark_callback_expired(self, sync_id: UUID) -> None:
        self._mark_callback_expired(sync_id)

    def _mark_callback_expired(self, sync_id: UUID) -> None:
        self._expired_sync_ids.add(sync_id)
        self._pending_callbacks.pop(sync_id, None)
        self._expected_sync_ids.discard(sync_id)
        self.cancel_orphan_callback_alarm(sync_id)

    def drop_orphan_callback(self, sync_id: UUID) -> None:
        self._pending_callbacks.pop(sync_id, None)
        self.cancel_orphan_callback_alarm(sync_id)
