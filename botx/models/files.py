"""Definition of file that can be included in incoming message or in sending result."""

import base64
from contextlib import contextmanager
from io import BytesIO
from pathlib import Path
from types import MappingProxyType
from typing import AnyStr, AsyncIterable, BinaryIO, Generator, Optional, TextIO, Union
from uuid import UUID

from base64io import Base64IO

from botx.models.base import BotXBaseModel
from botx.models.enums import AttachmentsTypes

EXTENSIONS_TO_MIMETYPES = MappingProxyType(
    {
        # application
        ".7z": "application/x-7z-compressed",
        ".abw": "application/x-abiword",
        ".ai": "application/postscript",
        ".arc": "application/x-freearc",
        ".azw": "application/vnd.amazon.ebook",
        ".bin": "application/octet-stream",
        ".bz": "application/x-bzip",
        ".bz2": "application/x-bzip2",
        ".cda": "application/x-cdf",
        ".csh": "application/x-csh",
        ".doc": "application/msword",
        ".docx": (
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        ),
        ".eot": "application/vnd.ms-fontobject",
        ".eps": "application/postscript",
        ".epub": "application/epub+zip",
        ".gz": "application/gzip",
        ".jar": "application/java-archive",
        ".json-api": "application/vnd.api+json",
        ".json-patch": "application/json-patch+json",
        ".json": "application/json",
        ".jsonld": "application/ld+json",
        ".mdb": "application/x-msaccess",
        ".mpkg": "application/vnd.apple.installer+xml",
        ".odp": "application/vnd.oasis.opendocument.presentation",
        ".ods": "application/vnd.oasis.opendocument.spreadsheet",
        ".odt": "application/vnd.oasis.opendocument.text",
        ".ogx": "application/ogg",
        ".pdf": "application/pdf",
        ".php": "application/x-httpd-php",
        ".ppt": "application/vnd.ms-powerpoint",
        ".pptx": (
            "application/vnd.openxmlformats-officedocument.presentationml.presentation"
        ),
        ".ps": "application/postscript",
        ".rar": "application/vnd.rar",
        ".rtf": "application/rtf",
        ".sh": "application/x-sh",
        ".swf": "application/x-shockwave-flash",
        ".tar": "application/x-tar",
        ".vsd": "application/vnd.visio",
        ".wasm": "application/wasm",
        ".webmanifest": "application/manifest+json",
        ".xhtml": "application/xhtml+xml",
        ".xls": "application/vnd.ms-excel",
        ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        ".xul": "application/vnd.mozilla.xul+xml",
        ".zip": "application/zip",
        # audio
        ".aac": "audio/aac",
        ".mid": "audio/midi",
        ".midi": "audio/midi",
        ".mp3": "audio/mpeg",
        ".oga": "audio/ogg",
        ".opus": "audio/opus",
        ".wav": "audio/wav",
        ".weba": "audio/webm",
        # font
        ".otf": "font/otf",
        ".ttf": "font/ttf",
        ".woff": "font/woff",
        ".woff2": "font/woff2",
        # image
        ".avif": "image/avif",
        ".bmp": "image/bmp",
        ".gif": "image/gif",
        ".ico": "image/vnd.microsoft.icon",
        ".jpeg": "image/jpeg",
        ".jpg": "image/jpeg",
        ".png": "image/png",
        ".svg": "image/svg+xml",
        ".svgz": "image/svg+xml",
        ".tif": "image/tiff",
        ".tiff": "image/tiff",
        ".webp": "image/webp",
        # text
        ".css": "text/css",
        ".csv": "text/csv",
        ".htm": "text/html",
        ".html": "text/html",
        ".ics": "text/calendar",
        ".js": "text/javascript",
        ".mjs": "text/javascript",
        ".txt": "text/plain",
        ".text": "text/plain",
        ".xml": "text/xml",
        # video
        ".3g2": "video/3gpp2",
        ".3gp": "video/3gpp",
        ".avi": "video/x-msvideo",
        ".mov": "video/quicktime",
        ".mp4": "video/mp4",
        ".mpeg": "video/mpeg",
        ".mpg": "video/mpeg",
        ".ogv": "video/ogg",
        ".ts": "video/mp2t",
        ".webm": "video/webm",
        ".wmv": "video/x-ms-wmv",
    },
)
DEFAULT_MIMETYPE = "application/octet-stream"


class NamedAsyncIterable(AsyncIterable):
    """AsyncIterable with `name` protocol."""

    name: str


class File(BotXBaseModel):  # noqa: WPS214
    """Object that represents file in RFC 2397 format."""

    #: name of file.
    file_name: str

    #: file content in RFC 2397 format.
    data: str  # noqa: WPS110

    #: text under file.
    caption: Optional[str] = None

    @classmethod
    def from_file(  # noqa: WPS210
        cls,
        file: Union[TextIO, BinaryIO],
        filename: Optional[str] = None,
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
        cls,
        file: NamedAsyncIterable,
        filename: Optional[str] = None,
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
            file,
            "__aiter__",
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
    def size_in_bytes(self) -> int:
        """Return file size in bytes."""
        with self.file_chunks() as chunks:
            return sum(len(chunk) for chunk in chunks)  # type: ignore

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
        return self._get_mimetype(self.file_name)

    @classmethod
    def get_ext_by_mimetype(cls, mimetype: str) -> Optional[str]:
        """Get extension by mimetype.

        Arguments:
            mimetype: mimetype of file.

        Returns:
            file extension or none if mimetype not found.
        """
        for ext, m_type in EXTENSIONS_TO_MIMETYPES.items():
            if m_type == mimetype:
                return ext

        return None

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
        file_extension = Path(filename).suffix.lower()
        return EXTENSIONS_TO_MIMETYPES.get(file_extension, DEFAULT_MIMETYPE)


class MetaFile(BotXBaseModel):
    """File info from file service."""

    #: type of file
    type: AttachmentsTypes

    #: file url.
    file: str

    #: mime type of file.
    file_mime_type: str

    #: name of file.
    file_name: str

    #: file preview.
    file_preview: Optional[str]

    #: height of file (px).
    file_preview_height: Optional[int]

    #: width of file (px).
    file_preview_width: Optional[int]

    #: size of file.
    file_size: int

    #: hash of file.
    file_hash: str

    #: encryption algorithm of file.
    file_encryption_algo: str

    #: chunks size.
    chunk_size: int

    #: ID of file.
    file_id: UUID

    #: file caption.
    caption: Optional[str]

    #: media file duration.
    duration: Optional[int]
