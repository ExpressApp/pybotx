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
        self.message = f"No bot account with bot_id: `{bot_id}`"
        super().__init__(self.message)
