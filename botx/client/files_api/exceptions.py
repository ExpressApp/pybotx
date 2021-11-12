from botx.client.exceptions.base import BaseClientException


class FileDeletedError(BaseClientException):
    """File deleted."""


class FileMetadataNotFound(BaseClientException):
    """Can't find file metadata."""
