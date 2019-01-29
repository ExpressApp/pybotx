# @TODO: Add serialization


class Status:

    def __init__(self, status='ok', result=None):
        self.status = status
        self.result = result


class StatusResult:

    def __init__(self, enabled=True, status_message='Bot is working',
                 commands=None):
        self.enabled = enabled
        self.status_message = status_message
        self.commands = commands if commands else []
