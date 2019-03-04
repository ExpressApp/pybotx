from botx import BotXObject


class ResponseCommand(BotXObject):
    def __init__(self, bot_id, sync_id, command_result, recipients="all"):
        self.bot_id = bot_id
        self.sync_id = sync_id
        self.command_result = command_result
        self.recipients = recipients


class ResponseCommandResult(BotXObject):
    def __init__(
        self,
        status="ok",
        body=None,
        commands=None,
        bubble=None,
        keyboard=None,
        files=None,
    ):
        self.status = status
        self.body = body if body else ""
        self.commands = commands if commands else []
        self.bubble = bubble if bubble else []
        self.keyboard = keyboard if keyboard else []
        self.files = files if files else []


class ResponseNotification(BotXObject):
    def __init__(self, bot_id, notification, group_chat_ids=None, recipients="all"):
        self.bot_id = bot_id
        self.notification = notification
        self.group_chat_ids = group_chat_ids if group_chat_ids else []
        self.recipients = recipients


class ResponseNotificationResult(ResponseCommandResult):
    pass


class ResponseDocument(BotXObject):
    def __init__(self, bot_id, sync_id):
        self.bot_id = bot_id
        self.sync_id = sync_id
