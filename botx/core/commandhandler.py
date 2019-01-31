class CommandHandler:
    ANY = True

    def __init__(self, command, func, name=None, description=None,
                 options=None, elements=None):
        self.command = command
        self.func = func
        self.name = name
        self.description = description
        self.options = options if options else {}
        self.elements = elements if elements else []

    # @TODO: Should CommandHandler be a BotXObject? No...
    def to_dict(self):
        _dict = self.__dict__

        if not _dict.get('name') or not _dict.get('description'):
            return

        _dict['body'] = _dict.get('command')
        _dict.pop('command')
        _dict.pop('func')
        return _dict
