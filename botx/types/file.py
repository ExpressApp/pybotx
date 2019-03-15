import base64
from io import BytesIO
from typing import BinaryIO, Union

from .base import BotXType


class File(BotXType):
    data: str
    file_name: str

    @property
    def file(self) -> Union[BinaryIO]:
        d = BytesIO(self.raw_data)
        d.name = self.file_name
        return d

    @property
    def raw_data(self) -> bytes:
        return base64.b64decode(self.data.split(",", 1)[1])
