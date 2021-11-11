from dataclasses import dataclass
from typing import List, Optional
from uuid import UUID

from pydantic import Field

from botx.shared_models.api_base import VerifiedPayloadBaseModel

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal  # type: ignore  # noqa: WPS440


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


class BotXAPISearchUserResult(VerifiedPayloadBaseModel):
    user_huid: UUID
    ad_login: Optional[str] = None
    ad_domain: Optional[str] = None
    name: str
    company: Optional[str] = None
    company_position: Optional[str] = None
    department: Optional[str] = None
    emails: List[str] = Field(default_factory=list)


class BotXAPISearchUserResponsePayload(VerifiedPayloadBaseModel):
    status: Literal["ok"]
    result: BotXAPISearchUserResult

    def to_domain(self) -> UserFromSearch:
        return UserFromSearch(
            huid=self.result.user_huid,
            ad_login=self.result.ad_login,
            ad_domain=self.result.ad_domain,
            username=self.result.name,
            company=self.result.company,
            company_position=self.result.company_position,
            department=self.result.department,
            emails=self.result.emails,
        )
