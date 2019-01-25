class CommandHandler:
    ANY = True

    def __init__(self, command, func, description=None):
        self.command = command
        self.func = func
        self.description = description
