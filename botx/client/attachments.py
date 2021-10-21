import base64
from types import MappingProxyType
from typing import Union

from botx.bot.models.outgoing_attachment import OutgoingAttachment
from botx.shared_models.api_base import UnverifiedPayloadBaseModel
from botx.shared_models.domain.attachments import IncomingContentAttachment

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


def encode_rfc2397(content: bytes, mimetype: str) -> str:
    b64_content = base64.b64encode(content).decode()
    return f"data:{mimetype};base64,{b64_content}"


class BotXAPIAttachment(UnverifiedPayloadBaseModel):
    file_name: str
    data: str

    @classmethod
    def from_file_attachment(
        cls,
        attachment: Union[IncomingContentAttachment, OutgoingAttachment],
    ) -> "BotXAPIAttachment":
        assert attachment.content is not None

        mimetype = EXTENSIONS_TO_MIMETYPES.get(
            attachment.filename.split(".")[-1],
            DEFAULT_MIMETYPE,
        )

        return cls(
            file_name=attachment.filename,
            data=encode_rfc2397(attachment.content, mimetype),
        )
