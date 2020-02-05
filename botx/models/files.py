"""Definition of file that can be included in incoming message or in sending result."""

import base64
import mimetypes
import pathlib
from io import BytesIO
from typing import AnyStr, BinaryIO, Optional, TextIO, Union

from pydantic import BaseModel, validator

"""File extensions that can be proceed by BotX API."""
BOTX_API_ACCEPTED_EXTENSIONS = (
    ".doc",
    ".docx",
    ".xls",
    ".xlsx",
    ".ppt",
    ".pptx",
    ".json",
    ".txt",
    ".pdf",
    ".html",
    ".jpg",
    ".jpeg",
    ".gif",
    ".png",
    ".mp3",
    ".mp4",
    ".rar",
    ".zip",
    ".7z",
    ".tar.gz",
    ".tar.bz2",
    ".gz",
    ".tgz",
)


class File(BaseModel):
    """Object that represents file in RFC 2397 format."""

    file_name: str
    """name of file."""
    data: str
    """file content in RFC 2397 format."""
    caption: Optional[str] = None
    """text under file."""

    @validator("file_name", always=True)
    def check_file_extension(cls, value: str) -> str:  # noqa: N805
        """Check that file extension can be handled by BotX API.

        Arguments:
            value: file name which will be checked for matching extensions.

        Returns:
            Passed name if matching was successful.
        """
        extensions_check = (
            value.lower().endswith(extension)
            for extension in BOTX_API_ACCEPTED_EXTENSIONS
        )

        if not any(extensions_check):
            raise ValueError(
                f"file {value} has an extensions that is not supported by BotX API"
            )

        return value

    @classmethod
    def from_file(
        cls, file: Union[TextIO, BinaryIO], filename: Optional[str] = None
    ) -> "File":
        """Convert file-like object into BotX API compatible file.

        Arguments:
            file: file-like object that will be used for creating file.
            filename: name that will be used for file, if was not passed, then will be
                retrieved from `file` `.name` property.

        Returns:
            Built file object.
        """
        filename = filename or pathlib.Path(file.name).name
        file_data = file.read()

        if isinstance(file_data, str):
            file_data = file_data.encode()

        data = base64.b64encode(file_data).decode()
        media_type = mimetypes.guess_type(filename)[0] or "text/plain"
        return cls(file_name=filename, data=f"data:{media_type};base64,{data}")

    @classmethod
    def from_string(cls, data: AnyStr, filename: str) -> "File":
        """Build file from bytes or string passed to method in `data` with `filename` as name.

        Arguments:
            data: string or bytes that will be used for creating file.
            filename: name for new file.

        Returns:
            Built file object.
        """
        if isinstance(data, str):
            file_data = data.encode()
        else:
            file_data = data
        file = BytesIO(file_data)
        file.name = filename
        return cls.from_file(file)

    @property
    def file(self) -> BinaryIO:
        """Return file data in file-like object that will return bytes."""
        bytes_file = BytesIO(self.data_in_bytes)
        bytes_file.name = self.file_name
        return bytes_file

    @property
    def data_in_bytes(self) -> bytes:
        """Return decoded file data in bytes."""
        return base64.b64decode(self.data_in_base64)

    @property
    def data_in_base64(self) -> str:
        """Return file data in base64 encoded string."""
        return self.data.split(",", 1)[1]

    @property
    def media_type(self) -> str:
        """Return media type of file."""
        return mimetypes.guess_type(self.data)[0] or "text/plain"
