from botx.base import BotXObject


class KeyboardElement(BotXObject):

    def __init__(self, command, label=None):
        self.command = command
        self.label = label if label else self.command


class ReplyKeyboardMarkup:

    def __init__(self, keyboard):
        self.keyboard = keyboard

    def to_list(self):
        data = []

        for row in self.keyboard:
            r = []
            for button in row:
                if not isinstance(button, KeyboardElement):
                    raise ValueError('`ReplyKeyboardMarkup` must contain only '
                                     '`KeyboardElement` objects')
                if hasattr(button, 'to_dict'):
                    r.append(button.to_dict())
                else:
                    r.append(button)
            data.append(r)

        return data
