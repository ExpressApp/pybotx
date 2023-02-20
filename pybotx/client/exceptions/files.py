from pybotx.client.exceptions.base import BaseClientError


class FileDeletedError(BaseClientError):
    """File deleted."""


class FileMetadataNotFound(BaseClientError):
    """Can't find file metadata."""


class FileTypeNotAllowed(BaseClientError):
    """File type is not allowed."""
