import base64
import mimetypes
import pathlib
from io import BytesIO
from typing import BinaryIO, TextIO, Union

from .base import BotXType


class File(BotXType):
    data: str
    file_name: str

    @classmethod
    def from_file(cls, file: Union[TextIO, BinaryIO]) -> "File":
        file_name = pathlib.Path(file.name).name
        file_data = file.read()

        if isinstance(file_data, str):
            file_data = file_data.encode()

        data = base64.b64encode(file_data).decode()
        media_type = mimetypes.guess_type(file_name)[0] or "text/plain"
        return File(file_name=file_name, data=f"data:{media_type};base64,{data}")

    @property
    def file(self) -> BinaryIO:
        bytes_data = BytesIO(self.raw_data)
        bytes_data.name = self.file_name
        return bytes_data

    @property
    def raw_data(self) -> bytes:
        return base64.b64decode(self.data.split(",", 1)[1])

    @property
    def media_type(self) -> str:
        return self.data.split("data:", 1)[1].split(";", 1)[0]
