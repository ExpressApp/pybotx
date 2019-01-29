from botx.types.other import ChatID


class Message:

    def __init__(self, chat_id, text, data, user_id, user_login, group_chat_id,
                 host, bot_id):
        self.chat_id = ChatID(chat_id)
        self.text = text
        self.data = data
        self.user_id = user_id
        self.user_login = user_login
        self.group_chat_id = group_chat_id
        self.host = host
        self.bot_id = bot_id

    @staticmethod
    def from_json(json_object):
        try:
            Message(chat_id=json_object['sync_id'],
                    text=json_object['command']['body'],
                    data=json_object['command']['data'],
                    user_id=json_object['from']['user_huid'],
                    user_login=json_object['from']['ad_login'],
                    group_chat_id=json_object['from']['group_chat_id'],
                    host=json_object['from']['host'],
                    bot_id=json_object['from']['bot_id'])
        except KeyError:
            return None
