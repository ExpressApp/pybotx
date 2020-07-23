"""Predefined mocked entities builder for routes."""
import uuid
from typing import Optional, Tuple

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
