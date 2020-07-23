"""Entities for users."""

from typing import List
from uuid import UUID

from pydantic import BaseModel

from botx.models.enums import UserKinds


class UserInChatCreated(BaseModel):
    """User that can be included in data in `system:chat_created` event."""

    #: user HUID.
    huid: UUID

    #: type of user.
    user_kind: UserKinds

    #: user username.
    name: str

    #: is user administrator in chat.
    admin: bool


class UserFromSearch(BaseModel):
    """User from search request."""

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


class UserFromChatSearch(BaseModel):
    """User from chat search request."""

    #: is user admin of chat.
    admin: bool

    #: HUID of user.
    user_huid: UUID

    #: type of user.
    user_kind: UserKinds
