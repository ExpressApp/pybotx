import os
import imghdr
import mimetypes

from botx.exception import BotXException


class InputFile:
    DEFAULT_MIME_TYPE = 'application/octet-stream'

    def __init__(self, file):
        self.input_file_content = file.read()
        self.filename = None

        if hasattr(file, 'name') and not isinstance(file.name, int):
            self.filename = os.path.basename(file.name)

        try:
            self.mimetype = InputFile.is_image(self.input_file_content)
        except BotXException:
            if self.filename:
                self.mimetype = mimetypes.guess_type(self.filename)[0] \
                                or InputFile.DEFAULT_MIME_TYPE
            else:
                self.mimetype = InputFile.DEFAULT_MIME_TYPE

        if not self.filename:
            self.filename = self.mimetype.replace('/', '.')

    @staticmethod
    def is_image(stream):
        image = imghdr.what(None, stream)
        if image:
            return image
        raise BotXException('Could not parse file content')

    @staticmethod
    def is_file(obj):
        return hasattr(obj, 'read')
