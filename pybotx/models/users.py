from dataclasses import dataclass
from typing import List, Optional
from uuid import UUID


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
    """

    huid: UUID
    ad_login: Optional[str]
    ad_domain: Optional[str]
    username: str
    company: Optional[str]
    company_position: Optional[str]
    department: Optional[str]
    emails: List[str]
