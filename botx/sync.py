import multiprocessing
from concurrent.futures.thread import ThreadPoolExecutor
from typing import Any, BinaryIO, Dict, Optional, TextIO, Union

from .bots import AsyncBot
from .dispatchers import AsyncDispatcher
from .execution import execute_callback_with_exception_catching
from .helpers import call_coroutine_as_function
from .models import (
    BotCredentials,
    Message,
    MessageMarkup,
    NotifyOptions,
    ReplyMessage,
    SendingCredentials,
    Status,
)

WORKERS_COUNT = multiprocessing.cpu_count() * 4


class SyncDispatcher(AsyncDispatcher):
    _pool: ThreadPoolExecutor

    def __init__(self, tasks_limit: int) -> None:
        super().__init__(0)
        self._pool = ThreadPoolExecutor(max_workers=tasks_limit)

    def start(self) -> None:  # type: ignore
        pass

    def shutdown(self) -> None:  # type: ignore
        self._pool.shutdown()

    def status(self) -> Status:
        return call_coroutine_as_function(super().status)

    def execute_command(self, data: Dict[str, Any]) -> None:  # type: ignore
        self._pool.submit(
            call_coroutine_as_function,
            execute_callback_with_exception_catching,
            self.exception_catchers,
            self._get_callback_copy_for_message_data(data),
        )


class SyncBot(AsyncBot):
    _dispatcher: SyncDispatcher

    def __init__(
        self,
        *,
        concurrent_tasks: int = WORKERS_COUNT,
        credentials: Optional[BotCredentials] = None,
    ) -> None:
        super().__init__(credentials=credentials)

        self._dispatcher = SyncDispatcher(concurrent_tasks)

    def start(self) -> None:  # type: ignore
        self._dispatcher.start()

    def stop(self) -> None:  # type: ignore
        self._dispatcher.shutdown()

    def status(self) -> Status:
        return self._dispatcher.status()

    def execute_command(self, data: Dict[str, Any]) -> None:  # type: ignore
        self._dispatcher.execute_command(data)

    def send_message(  # type: ignore
        self,
        text: str,
        credentials: SendingCredentials,
        *,
        file: Optional[Union[BinaryIO, TextIO]] = None,
        markup: Optional[MessageMarkup] = None,
        options: Optional[NotifyOptions] = None,
    ) -> None:
        return call_coroutine_as_function(
            super().send_message,
            text,
            credentials,
            file=file,
            markup=markup,
            options=options,
        )

    def answer_message(  # type: ignore
        self,
        text: str,
        message: Message,
        *,
        file: Optional[Union[BinaryIO, TextIO]] = None,
        markup: Optional[MessageMarkup] = None,
        options: Optional[NotifyOptions] = None,
    ) -> None:
        return call_coroutine_as_function(
            super().answer_message,
            text,
            message,
            file=file,
            markup=markup,
            options=options,
        )

    def reply(self, message: ReplyMessage) -> None:  # type: ignore
        return call_coroutine_as_function(super().reply, message)

    def send_file(  # type: ignore
        self, file: Union[TextIO, BinaryIO], credentials: SendingCredentials
    ) -> None:
        return call_coroutine_as_function(super().send_file, file, credentials)


Bot = SyncBot
