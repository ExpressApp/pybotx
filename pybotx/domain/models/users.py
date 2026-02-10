from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from pybotx.domain.models.enums import IncomingSyncSourceTypes, UserKinds


@dataclass(slots=True)
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
    ad_login: str | None
    ad_domain: str | None
    username: str
    company: str | None
    company_position: str | None
    department: str | None
    emails: list[str]
    other_id: str | None
    user_kind: UserKinds
    active: bool | None = None
    description: str | None = None
    ip_phone: str | None = None
    manager: str | None = None
    office: str | None = None
    other_ip_phone: str | None = None
    other_phone: str | None = None
    public_name: str | None = None
    cts_id: UUID | None = None
    rts_id: UUID | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


@dataclass(slots=True)
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
    email: str | None = None
    company: str | None = None
    department: str | None = None
    position: str | None = None
    avatar: str | None = None
    avatar_preview: str | None = None
    office: str | None = None
    manager: str | None = None
    manager_huid: UUID | None = None
    description: str | None = None
    phone: str | None = None
    other_phone: str | None = None
    ip_phone: str | None = None
    other_ip_phone: str | None = None
    personnel_number: str | None = None
