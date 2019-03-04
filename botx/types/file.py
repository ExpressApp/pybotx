from botx import BotXObject


class File(BotXObject):
    def __init__(self, data, file_name):
        self.data = data
        self.file_name = file_name

    @classmethod
    def from_json(cls, data):
        if not data:
            return
        data = super().from_json(data)
        return cls(**data)
