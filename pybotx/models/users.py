from dataclasses import dataclass
from typing import List, Optional
from uuid import UUID

from pybotx.models.enums import IncomingSyncSourceTypes, UserKinds


@dataclass
class UserFromSearch:
    """User from search.

    Attributes:
        huid: User huid.
        ad_login: User AD login.
        ad_domain: User AD domain.
        username: User name.
        company: User company.
        company_position: User company position.
        department: User department.
        emails: User emails.
        other_id: User other identificator.
        user_kind: User kind.
    """

    huid: UUID
    ad_login: Optional[str]
    ad_domain: Optional[str]
    username: str
    company: Optional[str]
    company_position: Optional[str]
    department: Optional[str]
    emails: List[str]
    other_id: Optional[str]
    user_kind: UserKinds


@dataclass
class UserFromCSV:
    """User from a list of a CTS users.

    Attributes:
        huid: User huid.
        ad_login: User AD login.
        ad_domain: User AD domain.
        username: User name.
        sync_source: Synchronization source.
        active: Is the user active or not.
        email: User email.
        company: User company.
        department: User department.
        position: User position.
    """

    huid: UUID
    ad_login: str
    ad_domain: str
    username: str
    sync_source: IncomingSyncSourceTypes
    active: bool
    user_kind: UserKinds
    email: Optional[str] = None
    company: Optional[str] = None
    department: Optional[str] = None
    position: Optional[str] = None
