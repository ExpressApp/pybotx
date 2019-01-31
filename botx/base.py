import json


class BotXObject:

    @classmethod
    def from_json(cls, data):
        if not data:
            return
        data = data.copy()
        return data

    def to_dict(self):
        data = {}

        for key in self.__dict__:
            value = self.__dict__[key]
            if value:
                if hasattr(value, 'to_dict'):
                    data[key] = value.to_dict()
                else:
                    data[key] = value

        return data
