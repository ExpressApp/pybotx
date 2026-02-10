from typing import Any

from pybotx.domain.errors import CallbackNotReceivedError
from pybotx.infrastructure.client.exceptions.base import BaseClientError
from pybotx.infrastructure.contracts.method_callbacks import BotAPIMethodFailedCallback


class BotXMethodFailedCallbackReceivedError(BaseClientError):
    """Callback with error received."""

    def __init__(self, callback: BotAPIMethodFailedCallback) -> None:
        exc = BaseClientError.from_callback(callback)
        self.callback = callback

        self.args = exc.args

    def __reduce__(self) -> Any:
        # This method required to pass exception from pybotx logger to bot logger.
        return type(self), (self.callback,)


__all__ = ("BotXMethodFailedCallbackReceivedError", "CallbackNotReceivedError")
