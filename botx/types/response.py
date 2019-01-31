from botx.base import BotXObject


class ResponseCommand(BotXObject):

    def __init__(self, sync_id, bot_id, command_result, recipients='all'):
        self.sync_id = sync_id
        self.recipients = recipients
        self.bot_id = bot_id
        self.command_result = command_result


class ResponseCommandResult(BotXObject):

    def __init__(self, status='ok', body=None, commands=None, bubble=None,
                 keyboard=None, files=None):
        self.status = status
        self.body = body if body else ''
        self.commands = commands if commands else []
        self.bubble = bubble if bubble else []
        self.keyboard = keyboard if keyboard else []
        self.files = files if files else []
