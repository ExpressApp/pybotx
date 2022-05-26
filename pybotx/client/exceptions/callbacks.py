from typing import Any
from uuid import UUID

from pybotx.client.exceptions.base import BaseClientError
from pybotx.models.method_callbacks import BotAPIMethodFailedCallback


class BotXMethodFailedCallbackReceivedError(BaseClientError):
    """Callback with error received."""

    def __init__(self, callback: BotAPIMethodFailedCallback) -> None:
        exc = BaseClientError.from_callback(callback)
        self.callback = callback

        self.args = exc.args

    def __reduce__(self) -> Any:
        # This method required to pass exception from pybotx logger to bot logger.
        return type(self), (self.callback,)  # pragma: no cover


class CallbackNotReceivedError(Exception):
    def __init__(self, sync_id: UUID) -> None:
        self.sync_id = sync_id
        self.message = f"Callback for sync_id `{sync_id}` hasn't been received"
        super().__init__(self.message)
