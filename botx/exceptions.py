class HandlerNotFoundException(Exception):
    """Handler for received command not found.

    Raises if bot received a command that does not have its own handler and no default
    handler is configured.
    """

    def __init__(self, command: str) -> None:
        self.command = command
        self.message = f"Handler for command `{command}` not found"
        super().__init__(self.message)
