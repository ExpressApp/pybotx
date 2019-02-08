from botx import BotXObject


class MessageCommand(BotXObject):

    def __init__(self, body=None, data=None):
        self.body = body
        self.data = data

    @classmethod
    def from_json(cls, data):
        if not data:
            return
        data = super().from_json(data)
        return cls(**data)


class StatusCommand(BotXObject):

    def __init__(self, body, name, description, options=None, elements=None):
        self.body = body
        self.name = name
        self.description = description
        self.options = options if options else {}
        self.elements = elements if elements else []


# @TODO: Add options for commands
class StatusCommandOptions(BotXObject):
    pass


# @TODO: Add elements for commands
class StatusCommandElements(BotXObject):
    pass
