from typing import List, Literal, Optional
from uuid import UUID

from pydantic import Field

from pybotx.models.api_base import VerifiedPayloadBaseModel
from pybotx.models.users import UserFromSearch


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
