"""Predefined mocked entities builder for routes."""
import uuid
from typing import Optional, Tuple

from botx.models.enums import AttachmentsTypes
from botx.models.files import MetaFile
from botx.models.users import UserFromSearch


def create_test_user(
    *,
    user_huid: Optional[uuid.UUID] = None,
    email: Optional[str] = None,
    ad: Optional[Tuple[str, str]] = None,
) -> UserFromSearch:
    """Build test user for using in search.

    Arguments:
        user_huid: HUID of user for search.
        email: email of user for search.
        ad: AD credentials of user for search.

    Returns:
        "Found" user.
    """
    return UserFromSearch(
        user_huid=user_huid or uuid.uuid4(),
        ad_login=ad[0] if ad else "ad_login",
        ad_domain=ad[1] if ad else "ad_domain",
        name="test user",
        company="test company",
        company_position="test position",
        department="test department",
        emails=[email or "test@example.com"],
    )


def create_test_metafile(filename: str = None) -> MetaFile:
    """Build test metafile for using in uploading.

    Arguments:
        filename: name of uploaded file.

    Returns:
        Metadata of uploaded file.
    """
    return MetaFile(
        type=AttachmentsTypes.image,
        file="https://service.to./image",
        file_mime_type="image/png",
        file_name=filename or "image.png",
        file_preview=None,
        file_preview_height=None,
        file_preview_width=None,
        file_size=100,
        file_hash="W1Sn1AkotkOpH0",
        file_encryption_algo="stream",
        chunk_size=10,
        file_id=uuid.UUID("8dada2c8-67a6-4434-9dec-570d244e78ee"),
        caption=None,
        duration=None,
    )
