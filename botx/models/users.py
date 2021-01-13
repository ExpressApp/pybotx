"""Entities for users."""

from typing import List, Optional
from uuid import UUID

from botx.models.base import BotXBaseModel
from botx.models.enums import UserKinds


class UserInChatCreated(BotXBaseModel):
    """User that can be included in data in `system:chat_created` event."""

    #: user HUID.
    huid: UUID

    #: type of user.
    user_kind: UserKinds

    #: user username.
    name: Optional[str]

    #: is user administrator in chat.
    admin: bool


class UserFromSearch(BotXBaseModel):
    """User from search request."""

    #: HUID of user from search.
    user_huid: UUID

    #: AD login of user.
    ad_login: Optional[str]

    # AD domain of user.
    ad_domain: Optional[str]

    #: visible username.
    name: str

    #: user's company.
    company: Optional[str]

    #: user's position.
    company_position: Optional[str]

    #: user's department.
    department: Optional[str]

    #: user's emails.
    emails: List[str]


class UserFromChatSearch(BotXBaseModel):
    """User from chat search request."""

    #: is user admin of chat.
    admin: bool

    #: HUID of user.
    user_huid: UUID

    #: type of user.
    user_kind: UserKinds
