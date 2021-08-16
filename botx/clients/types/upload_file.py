"""Uploading file metadata."""
from typing import Optional

from pydantic import BaseModel


class UploadingFileMeta(BaseModel):
    """Uploading file metadata."""

    #: duration of media file
    duration: Optional[int] = None

    #: caption of media file
    caption: Optional[str] = None
