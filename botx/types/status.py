from botx import BotXObject


class Status(BotXObject):

    def __init__(self, status='ok', result=None):
        self.status = status
        self.result = result


class StatusResult(BotXObject):

    def __init__(self, enabled=True, status_message='Bot is working',
                 commands=None):
        self.enabled = enabled
        self.status_message = status_message
        self.commands = commands if commands else []
