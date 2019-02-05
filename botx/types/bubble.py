from botx.base import BotXObject


class BubbleElement(BotXObject):

    def __init__(self, command, label=None):
        self.command = command
        self.label = label if label else self.command


class ReplyBubbleMarkup:

    def __init__(self, keyboard):
        self.keyboard = keyboard

    def to_list(self):
        data = []

        for row in self.keyboard:
            r = []
            for button in row:
                if not isinstance(button, BubbleElement):
                    raise ValueError('`ReplyBubbleMarkup` must contain only '
                                     '`BubbleElement` objects')
                if hasattr(button, 'to_dict'):
                    r.append(button.to_dict())
                else:
                    r.append(button)
            data.append(r)

        return data
