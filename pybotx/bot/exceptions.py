from typing import Any
from uuid import UUID


class UnknownBotAccountError(Exception):
    def __init__(self, bot_id: UUID) -> None:
        self.bot_id = bot_id
        self.message = f"No bot account with bot_id: `{bot_id!s}`"
        super().__init__(self.message)


class BotXMethodCallbackNotFoundError(Exception):
    def __init__(self, sync_id: UUID) -> None:
        self.sync_id = sync_id
        self.message = (
            f"Callback `{sync_id}` doesn't exist or already waited or timed out"
        )
        super().__init__(self.message)


class BotShuttingDownError(Exception):
    def __init__(self, context: Any) -> None:
        self.context = context
        self.message = f"Bot is shutting down: {context}"
        super().__init__(self.message)


class AnswerDestinationLookupError(Exception):
    def __init__(self) -> None:
        self.message = "No IncomingMessage received. Use `Bot.send` instead"
        super().__init__(self.message)
