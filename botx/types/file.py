from io import BytesIO

from .base import BotXType


class File(BotXType):
    data: str
    file_name: str

    @property
    def file(self):
        return BytesIO(self.data.encode("utf-8"))
