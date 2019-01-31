from botx.base import BotXObject
from botx.types.other import SyncID
from botx.types.command import MessageCommand


class Message(BotXObject):

    def __init__(self, sync_id, command, from_, bot_id):
        self.sync_id = SyncID(sync_id)
        self.command = command
        self.from_ = from_
        self.bot_id = bot_id

    @property
    def body(self):
        return self.command.body

    @property
    def data(self):
        return self.command.data

    @property
    def user_huid(self):
        return self.from_.user_huid

    @property
    def group_chat_id(self):
        return self.from_.group_chat_id

    @property
    def ad_login(self):
        return self.from_.ad_login

    @property
    def host(self):
        return self.from_.host

    @classmethod
    def from_json(cls, data):
        if not data:
            return

        data = super(Message, cls).from_json(data)

        data['command'] = MessageCommand.from_json(data.get('command'))
        data['from_'] = From.from_json(data.get('from'))

        return cls(**data)


class From(BotXObject):

    def __init__(self, user_huid, group_chat_id, ad_login, host):
        self.user_huid = user_huid
        self.group_chat_id = group_chat_id
        self.ad_login = ad_login
        self.host = host

    @classmethod
    def from_json(cls, data):
        if not data:
            return
        data = super(From, cls).from_json(data)
        return cls(**data)
