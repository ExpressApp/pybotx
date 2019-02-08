# import os
import imghdr
# import mimetypes


class InputFile:
    DEFAULT_MIME_TYPE = 'application/octet-stream'

    @staticmethod
    def is_image(stream):
        image = imghdr.what(None, stream)
        if image:
            return image
        return

    @staticmethod
    def is_file(obj):
        return hasattr(obj, 'read')
