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

            if hasattr(value, "to_dict"):
                data[key] = value.to_dict()
            elif isinstance(value, list):
                temp_value = []
                for item in value:
                    if hasattr(item, "to_dict"):
                        temp_value.append(item.to_dict())
                    else:
                        temp_value.append(item)
                data[key] = temp_value
            else:
                data[key] = value

        return data
