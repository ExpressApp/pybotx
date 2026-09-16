from typing import Any

from pybotx.models.message.incoming_message import IncomingMessage

from .base import Widget

ASYNC_JOB_ID_KEY = "async_job_id"
ASYNC_JOB_STATUS_KEY = "async_job_status"
ASYNC_JOB_ACTION_KEY = "async_job_action"

ASYNC_JOB_QUEUED = "queued"
ASYNC_JOB_RUNNING = "running"
ASYNC_JOB_DONE = "done"
ASYNC_JOB_FAILED = "failed"
ASYNC_JOB_CANCELLED = "cancelled"

ASYNC_JOB_ACTION_REFRESH = "refresh"
ASYNC_JOB_ACTION_RETRY = "retry"
ASYNC_JOB_ACTION_CANCEL = "cancel"


class AsyncJobWidget(Widget):
    def __init__(
        self,
        job_id: str,
        status: str,
        details: str = "",
        *args: Any,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.job_id = job_id
        self.status = status
        self.details = details
        self.widget_message.body = self._build_body()
        self.widget_metadata[ASYNC_JOB_ID_KEY] = self.job_id
        self.widget_metadata[ASYNC_JOB_STATUS_KEY] = self.status

    def add_markup(self) -> None:
        if self.status in {ASYNC_JOB_QUEUED, ASYNC_JOB_RUNNING}:
            self.widget_bubbles.add_button(
                command=self.command,
                label="Обновить",
                data={ASYNC_JOB_ACTION_KEY: ASYNC_JOB_ACTION_REFRESH},
            )
            self.widget_bubbles.add_button(
                command=self.command,
                label="Отменить",
                data={ASYNC_JOB_ACTION_KEY: ASYNC_JOB_ACTION_CANCEL},
                new_row=False,
            )
            self.add_additional_markup()
            return

        if self.status == ASYNC_JOB_FAILED:
            self.widget_bubbles.add_button(
                command=self.command,
                label="Повторить",
                data={ASYNC_JOB_ACTION_KEY: ASYNC_JOB_ACTION_RETRY},
            )

        self.widget_bubbles.add_button(
            command=self.command,
            label="Обновить",
            data={ASYNC_JOB_ACTION_KEY: ASYNC_JOB_ACTION_REFRESH},
            new_row=self.status != ASYNC_JOB_FAILED,
        )
        self.add_additional_markup()

    def _build_body(self) -> str:
        body = f"Задача {self.job_id}\nСтатус: {self.status}"
        if self.details:
            body = f"{body}\n{self.details}"
        return body

    @classmethod
    def get_action(cls, message: IncomingMessage) -> str:
        action = message.data.get(ASYNC_JOB_ACTION_KEY)
        if action not in {
            ASYNC_JOB_ACTION_REFRESH,
            ASYNC_JOB_ACTION_RETRY,
            ASYNC_JOB_ACTION_CANCEL,
        }:
            raise RuntimeError("Async job action is not found.")

        return str(action)

    @classmethod
    def get_status(cls, message: IncomingMessage) -> str:
        status = message.metadata.get(ASYNC_JOB_STATUS_KEY)
        if status is None:
            raise RuntimeError("Async job status is not found.")
        return str(status)
