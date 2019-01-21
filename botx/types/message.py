class Message:

    def __init__(self, sync_id, text, data, user_id, user_login, group_chat_id,
                 host, bot_id):
        self.sync_id = sync_id
        self.text = text
        self.data = data
        self.user_id = user_id
        self.user_login = user_login
        self.group_chat_id = group_chat_id
        self.host = host
        self.bot_id = bot_id
