from uuid import UUID

from botx.bot.models.method_callbacks import BotAPIMethodFailedCallback


class BotXMethodFailedCallbackReceivedError(Exception):
    def __init__(self, callback: BotAPIMethodFailedCallback) -> None:
        self.callback = callback
        self.message = (
            f"BotX method call with sync_id `{callback.sync_id!s}` "
            f"failed with: {callback}"
        )
        super().__init__(self.message)


class CallbackNotReceivedError(Exception):
    def __init__(self, sync_id: UUID) -> None:
        self.sync_id = sync_id
        self.message = f"Callback for sync_id `{sync_id}` hasn't been received"
        super().__init__(self.message)