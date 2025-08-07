import asyncio
import threading
from typing import TYPE_CHECKING, Dict, Optional
from uuid import UUID

from pybotx.bot.callbacks.callback_repo_proto import CallbackRepoProto
from pybotx.bot.exceptions import BotShuttingDownError, BotXMethodCallbackNotFoundError
from pybotx.client.exceptions.callbacks import CallbackNotReceivedError
from pybotx.models.method_callbacks import BotXMethodCallback

if TYPE_CHECKING:
    from asyncio import Future  # noqa: WPS458


class CallbackWrapper:
    """Thread-safe wrapper for callback operations across different event loops."""

    def __init__(
        self, sync_id: UUID, main_loop: Optional[asyncio.AbstractEventLoop] = None
    ):
        self.sync_id = sync_id
        self.main_loop = main_loop
        self._result = None
        self._exception = None
        self._event = threading.Event()
        self._future: Optional["Future[BotXMethodCallback]"] = None

    def create_future(self) -> None:
        """Create the asyncio Future in the appropriate event loop."""
        if self.main_loop is not None:
            try:
                current_loop = asyncio.get_running_loop()
                if self.main_loop == current_loop:
                    self._future = asyncio.Future()
                else:

                    def create_future():
                        self._future = asyncio.Future()

                    self.main_loop.call_soon_threadsafe(create_future)
            except RuntimeError:
                if self.main_loop is not None:

                    def create_future():
                        self._future = asyncio.Future()

                    self.main_loop.call_soon_threadsafe(create_future)
                else:
                    self._future = asyncio.Future()
        else:
            self._future = asyncio.Future()

    def set_result(self, result) -> None:
        """Set the result in a thread-safe manner."""
        self._result = result
        self._event.set()

        if self._future is not None and not self._future.done():
            if self.main_loop is not None:
                try:
                    current_loop = asyncio.get_running_loop()
                    if self.main_loop == current_loop:
                        self._future.set_result(result)
                    else:
                        self.main_loop.call_soon_threadsafe(
                            self._future.set_result, result
                        )
                except RuntimeError:
                    self.main_loop.call_soon_threadsafe(self._future.set_result, result)
            else:
                self._future.set_result(result)

    def set_exception(self, exception) -> None:
        """Set an exception in a thread-safe manner."""
        self._exception = exception
        self._event.set()

        # Also set the Future exception if it exists
        if self._future is not None and not self._future.done():
            if self.main_loop is not None:
                try:
                    current_loop = asyncio.get_running_loop()
                    if self.main_loop == current_loop:
                        self._future.set_exception(exception)
                    else:
                        self.main_loop.call_soon_threadsafe(
                            self._future.set_exception, exception
                        )
                except RuntimeError:
                    self.main_loop.call_soon_threadsafe(
                        self._future.set_exception, exception
                    )
            else:
                self._future.set_exception(exception)

    async def wait_for_result(self, timeout: float):
        """Wait for the result with timeout."""
        try:
            current_loop = asyncio.get_running_loop()
            if (
                self.main_loop is not None
                and self.main_loop == current_loop
                and self._future is not None
            ):
                return await asyncio.wait_for(self._future, timeout=timeout)
            else:

                def wait_with_timeout():
                    return self._event.wait(timeout)

                loop = asyncio.get_running_loop()
                success = await loop.run_in_executor(None, wait_with_timeout)

                if not success:
                    raise asyncio.TimeoutError()

                if self._exception is not None:
                    raise self._exception

                return self._result
        except RuntimeError:
            success = self._event.wait(timeout)
            if not success:
                raise asyncio.TimeoutError()

            if self._exception is not None:
                raise self._exception

            return self._result

    def get_future(self) -> "Future[BotXMethodCallback]":
        """Get the underlying Future object."""
        if self._future is None:
            raise RuntimeError("Future not created")
        return self._future


class CallbackMemoryRepo(CallbackRepoProto):
    def __init__(self) -> None:
        self._callback_wrappers: Dict[UUID, CallbackWrapper] = {}
        self._main_loop: Optional[asyncio.AbstractEventLoop] = None

    def set_main_loop(self, loop: asyncio.AbstractEventLoop) -> None:
        """Set the main event loop to use for callback operations."""
        self._main_loop = loop

    def _get_event_loop(self) -> asyncio.AbstractEventLoop:
        """Get the event loop to use for callback operations."""
        if self._main_loop is not None:
            return self._main_loop
        return asyncio.get_event_loop()

    async def create_botx_method_callback(self, sync_id: UUID) -> None:
        wrapper = CallbackWrapper(sync_id, self._main_loop)
        wrapper.create_future()
        self._callback_wrappers[sync_id] = wrapper

    async def set_botx_method_callback_result(
        self,
        callback: BotXMethodCallback,
    ) -> None:
        sync_id = callback.sync_id

        wrapper = self._get_botx_method_callback_wrapper(sync_id)
        wrapper.set_result(callback)

    async def wait_botx_method_callback(
        self,
        sync_id: UUID,
        timeout: float,
    ) -> BotXMethodCallback:
        wrapper = self._get_botx_method_callback_wrapper(sync_id)

        try:
            return await wrapper.wait_for_result(timeout)
        except asyncio.TimeoutError as exc:
            del self._callback_wrappers[sync_id]  # noqa: WPS420
            raise CallbackNotReceivedError(sync_id) from exc

    async def pop_botx_method_callback(
        self,
        sync_id: UUID,
    ) -> "Future[BotXMethodCallback]":
        wrapper = self._callback_wrappers.pop(sync_id)
        return wrapper.get_future()

    async def stop_callbacks_waiting(self) -> None:
        for sync_id, wrapper in self._callback_wrappers.items():
            exception = BotShuttingDownError(
                f"Callback with sync_id `{sync_id!s}` can't be received",
            )
            wrapper.set_exception(exception)

    def _get_botx_method_callback_wrapper(self, sync_id: UUID) -> CallbackWrapper:
        try:
            return self._callback_wrappers[sync_id]
        except KeyError:
            raise BotXMethodCallbackNotFoundError(sync_id) from None
