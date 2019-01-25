class Response:
    # @TODO: Add json serialization from classes

    def __init__(self, chat_id=None, group_chat_ids=None, recipients='all',
                 bot_id=None, body=None):
        # @TODO: Add other types, ^delete body and add it to another type
        if chat_id and group_chat_ids:
            raise ValueError('`chat_id` and `group_chat_ids` both can not be '
                             'provided at the same time')
        self.chat_id = chat_id
        self.group_chat_ids = group_chat_ids
        self.recipients = recipients
        self.bot_id = bot_id
        self.body = body

    def to_json(self):
        return {
            'sync_id': self.chat_id,
            'recipients': self.recipients,
            'bot_id': self.bot_id,
            'command_result': {
                'status': 'ok',
                'body': self.body,
                'commands': [],
                'bubble': [],
                'keyboard': [],
                'files': []
            }
        }
