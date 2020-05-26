from typing import List
from uuid import UUID

from pydantic import BaseModel


class UserFromSearch(BaseModel):
    user_huid: UUID
    ad_login: str
    ad_domain: str
    name: str
    company: str
    company_position: str
    department: str
    emails: List[str]
