"""Definition of file that can be included in incoming message or in sending result."""

import base64
import mimetypes
from contextlib import contextmanager
from io import BytesIO
from pathlib import Path
from typing import AnyStr, AsyncIterable, BinaryIO, Generator, Optional, TextIO, Union

from base64io import Base64IO
from pydantic import BaseModel, validator

#: file extensions that can be proceed by BotX API.
BOTX_API_ACCEPTED_EXTENSIONS = (
    # image extensions
    ".jpg",
    ".jpeg",
    ".gif",
    ".png",
    # document extensions
    ".doc",
    ".docx",
    ".xls",
    ".xlsx",
    ".txt",
    ".pdf",
    ".html",
    ".json",
    ".sig",
    ".ppt",
    ".pptx",
    # media extensions
    ".mp3",
    ".mp4",
    # archive extensions
    ".gz",
    ".tgz",
    ".zip",
    ".rar",
)


class NamedAsyncIterable(AsyncIterable):
    """AsyncIterable with `name` protocol."""

    name: str


class File(BaseModel):  # noqa: WPS214
    """Object that represents file in RFC 2397 format."""

    #: name of file.
    file_name: str

    #: file content in RFC 2397 format.
    data: str  # noqa: WPS110

    #: text under file.
    caption: Optional[str] = None

    @validator("file_name", always=True)
    def check_file_extension(cls, name: str) -> str:  # noqa: N805
        """Check that file extension can be handled by BotX API.

        Arguments:
            name: file name which will be checked for matching extensions.

        Returns:
            Passed name if matching was successful.

        Raises:
            ValueError: raised if extension is not supported.
        """
        if not cls.has_supported_extension(name):
            raise ValueError(
                "file {0} has an extensions that is not supported by BotX API".format(
                    name,
                ),
            )

        return name

    @classmethod
    def from_file(  # noqa: WPS210
        cls, file: Union[TextIO, BinaryIO], filename: Optional[str] = None,
    ) -> "File":
        """Convert file-like object into BotX API compatible file.

        Arguments:
            file: file-like object that will be used for creating file.
            filename: name that will be used for file, if was not passed, then will be
                retrieved from `file` `.name` property.

        Returns:
            Built file object.
        """
        filename = filename or Path(file.name).name
        encoded_file = BytesIO()

        text_mode = file.read(0) == ""  # b"" if bytes mode

        with Base64IO(encoded_file) as b64_stream:
            if text_mode:
                for text_line in file:  # TODO: Deprecate text mode in 0.17
                    b64_stream.write(text_line.encode())  # type: ignore
            else:
                for line in file:
                    b64_stream.write(line)

        encoded_file.seek(0)
        encoded_data = encoded_file.read().decode()

        media_type = cls._get_mimetype(filename)
        return cls(file_name=filename, data=cls._to_rfc2397(media_type, encoded_data))

    @classmethod
    async def async_from_file(  # noqa: WPS210
        cls, file: NamedAsyncIterable, filename: Optional[str] = None,
    ) -> "File":
        """Convert async file-like object into BotX API compatible file.

        Arguments:
            file: async file-like object that will be used for creating file.
            filename: name that will be used for file, if was not passed, then will be
                retrieved from `file` `.name` property.

        Returns:
            Built File object.
        """
        assert hasattr(  # noqa: WPS421
            file, "__aiter__",
        ), "file should support async iteration"

        filename = filename or Path(file.name).name
        media_type = cls._get_mimetype(filename)

        encoded_file = BytesIO()

        with Base64IO(encoded_file) as b64_stream:
            async for line in file:  # pragma: no branch
                b64_stream.write(line)

        encoded_file.seek(0)
        encoded_data = encoded_file.read().decode()

        return cls(file_name=filename, data=cls._to_rfc2397(media_type, encoded_data))

    @contextmanager
    def file_chunks(self) -> Generator[bytes, None, None]:
        """Return file data in iterator that will return bytes."""
        encoded_file = BytesIO(self.data_in_base64.encode())

        with Base64IO(encoded_file) as decoded_file:
            yield decoded_file

    @classmethod
    def from_string(cls, data_of_file: AnyStr, filename: str) -> "File":
        """Build file from bytes or string passed to method in `data` with `filename` as name.

        Arguments:
            data_of_file: string or bytes that will be used for creating file.
            filename: name for new file.

        Returns:
            Built file object.
        """
        if isinstance(data_of_file, str):
            file_data = data_of_file.encode()
        else:
            file_data = data_of_file
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
        return self._get_mimetype(self.data)

    @classmethod
    def has_supported_extension(cls, filename: str) -> bool:
        """Check that file extension can be handled by BotX API.

        Arguments:
            filename: file name to check.

        Returns:
            Matching result.
        """
        file_extension = Path(filename).suffix.lower()
        return file_extension in BOTX_API_ACCEPTED_EXTENSIONS

    @classmethod
    def _to_rfc2397(cls, media_type: str, encoded_data: str) -> str:
        """Apply RFC 2397 format to encoded file contents.

        Arguments:
            media_type: file media type.
            encoded_data: base64 encoded file contents.

        Returns:
            File contents converted to RFC 2397.
        """
        return "data:{0};base64,{1}".format(media_type, encoded_data)

    @classmethod
    def _get_mimetype(cls, filename: str) -> str:
        """Get mimetype by filename.

        Arguments:
            filename: file name to inspect.

        Returns:
            File mimetype.
        """
        return mimetypes.guess_type(filename)[0] or "text/plain"
