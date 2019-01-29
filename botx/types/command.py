class Command:
    ANY = True

    def __init__(self, command, func, name, description, options=None,
                 elements=None):
        """
        :param command: A command (e.g. `/start`)
         :type command: str or bool
        :param func: A name of the function to call for
         :type func: function
        :param name: A name of the command (e.g. `Start the Bot`)
         :type name: str
        :param description: A description of the command
         :type description: str
        :param options: Options
         :type options: dict
        :param elements: Elements
         :type elements: list
        """
        self.command = command
        self.func = func
        self.name = name
        self.description = description
        self.options = options if options else {}
        self.elements = elements if elements else []

    def to_dict(self):
        _dict = self.__dict__
        if self.command == Command.ANY:
            try:
                _dict['command'] = 'any'
            except KeyError as err:
                raise err
        _dict.pop('func')
        return _dict


# @TODO: Add elements for commands
class CommandElements:
    pass
