"""Entities for chats."""

from typing import List
from uuid import UUID

from pydantic import BaseModel


class UserFromSearch(BaseModel):
    """Chat from search request."""

    #: HUID of user from search.
    user_huid: UUID

    #: AD login of user.
    ad_login: str

    # AD domain of user.
    ad_domain: str

    #: visible username.
    name: str

    #: user's company.
    company: str

    #: user's position.
    company_position: str

    #: user's department.
    department: str

    #: user's emails.
    emails: List[str]
