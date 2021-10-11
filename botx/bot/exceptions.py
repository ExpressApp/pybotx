from typing import Any
from uuid import UUID


class HandlerNotFoundError(Exception):
    """Handler for received command not found.

    Raises if bot received a command that does not have its own handler and no default
    handler is configured.
    """

    def __init__(self, command: str) -> None:
        self.command = command
        self.message = f"Handler for command `{command}` not found"
        super().__init__(self.message)


class UnknownBotAccountError(Exception):
    def __init__(self, bot_id: UUID) -> None:
        self.bot_id = bot_id
        self.message = f"No bot account with bot_id: `{bot_id!s}`"
        super().__init__(self.message)


class BotXMethodCallbackNotFound(Exception):
    def __init__(self, sync_id: UUID) -> None:
        self.sync_id = sync_id
        self.message = f"No callback found with sync_id: `{sync_id!s}`"
        super().__init__(self.message)


class BotShuttignDownError(Exception):
    def __init__(self, context: Any) -> None:
        self.context = context
        self.message = f"Bot is shutting down: {context}"
        super().__init__(self.message)
