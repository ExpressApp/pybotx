from dataclasses import dataclass
from datetime import datetime
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
        active: User active status.
        description: User description.
        ip_phone: User IP phone.
        manager: User manager.
        office: User office.
        other_ip_phone: User other IP phone.
        other_phone: User other phone.
        public_name: User public name.
        cts_id: User CTS id.
        rts_id: User RTS id.
        created_at: User creation timestamp.
        updated_at: User update timestamp.
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
    active: Optional[bool] = None
    description: Optional[str] = None
    ip_phone: Optional[str] = None
    manager: Optional[str] = None
    office: Optional[str] = None
    other_ip_phone: Optional[str] = None
    other_phone: Optional[str] = None
    public_name: Optional[str] = None
    cts_id: Optional[UUID] = None
    rts_id: Optional[UUID] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


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
        avatar: Src to full avatar.
        avatar_preview: Src to avatar.
        office: Office info.
        manager: User's manager full name.
        manager_huid: User's manager huid.
        description: Description.
        phone: Phone number.
        other_phone: Extra phone number.
        ip_phone: Ip phone info.
        other_ip_phone: Extra ip phone.
        personnel_number: User's tabel number.
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
    avatar: Optional[str] = None
    avatar_preview: Optional[str] = None
    office: Optional[str] = None
    manager: Optional[str] = None
    manager_huid: Optional[UUID] = None
    description: Optional[str] = None
    phone: Optional[str] = None
    other_phone: Optional[str] = None
    ip_phone: Optional[str] = None
    other_ip_phone: Optional[str] = None
    personnel_number: Optional[str] = None
