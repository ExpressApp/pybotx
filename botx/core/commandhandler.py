from botx.types import StatusCommand


class CommandHandler:
    ANY = True

    def __init__(
        self, command, func, name=None, description=None, options=None, elements=None
    ):
        self.command = command
        self.func = func
        self.name = name
        self.description = description
        self.options = options if options else {}
        self.elements = elements if elements else []

    @property
    def is_status_command_compatible(self):
        if self.command and self.name and self.description:
            return True
        return False

    def to_status_command(self):
        if self.is_status_command_compatible:
            command = self.command if self.command != CommandHandler.ANY else "any"
            # if not isinstance(command, str):
            #     raise ValueError('A `command` must be a type of str')
            # if command.strip().startswith('/'):
            #     command = command[1:]

            return StatusCommand(
                body=command,
                name=self.name,
                description=self.description,
                options=self.options,
                elements=self.elements,
            )
        return

    def to_dict(self):
        _dict = self.__dict__

        if not _dict.get("name") or not _dict.get("description"):
            return

        _dict["body"] = _dict.get("command")
        _dict.pop("command")
        _dict.pop("func")
        return _dict
