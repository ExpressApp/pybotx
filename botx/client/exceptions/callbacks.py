from uuid import UUID

from botx.client.exceptions.base import BaseClientError
from botx.models.method_callbacks import BotAPIMethodFailedCallback


class BotXMethodFailedCallbackReceivedError(BaseClientError):
    """Callback with error received."""

    def __init__(self, callback: BotAPIMethodFailedCallback) -> None:
        exc = BaseClientError.from_callback(callback)
        self.args = exc.args


class CallbackNotReceivedError(Exception):
    def __init__(self, sync_id: UUID) -> None:
        self.sync_id = sync_id
        self.message = f"Callback for sync_id `{sync_id}` hasn't been received"
        super().__init__(self.message)
