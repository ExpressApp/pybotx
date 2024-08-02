from datetime import datetime
from typing import List, Literal, Optional
from uuid import UUID

from pydantic import Field

from pybotx.models.api_base import VerifiedPayloadBaseModel
from pybotx.models.enums import APIUserKinds, convert_user_kind_to_domain
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
    other_id: Optional[str] = None
    user_kind: APIUserKinds
    active: Optional[bool] = None
    description: Optional[str] = None
    ip_phone: Optional[int] = None
    manager: Optional[str] = None
    office: Optional[str] = None
    other_ip_phone: Optional[int] = None
    other_phone: Optional[int] = None
    public_name: Optional[str] = None
    cts_id: Optional[UUID] = None
    rts_id: Optional[UUID] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


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
            other_id=self.result.other_id,
            user_kind=convert_user_kind_to_domain(self.result.user_kind),
            active=None if self.result.active is None else bool(self.result.active),
            description=self.result.description,
            ip_phone=self.result.ip_phone,
            manager=self.result.manager,
            office=self.result.office,
            other_ip_phone=self.result.other_ip_phone,
            other_phone=self.result.other_phone,
            public_name=self.result.public_name,
            cts_id=self.result.cts_id,
            rts_id=self.result.rts_id,
            created_at=self.result.created_at,
            updated_at=self.result.updated_at,
        )


class BotXAPISearchUserByEmailsResponsePayload(VerifiedPayloadBaseModel):
    status: Literal["ok"]
    result: List[BotXAPISearchUserResult]

    def to_domain(self) -> List[UserFromSearch]:
        return [
            UserFromSearch(
                huid=user.user_huid,
                ad_login=user.ad_login,
                ad_domain=user.ad_domain,
                username=user.name,
                company=user.company,
                company_position=user.company_position,
                department=user.department,
                emails=user.emails,
                other_id=user.other_id,
                user_kind=convert_user_kind_to_domain(user.user_kind),
                active=None if user.active is None else bool(user.active),
                created_at=user.created_at,
                cts_id=user.cts_id,
                description=user.description,
                ip_phone=user.ip_phone,
                manager=user.manager,
                office=user.office,
                other_ip_phone=user.other_ip_phone,
                other_phone=user.other_phone,
                public_name=user.public_name,
                rts_id=user.rts_id,
                updated_at=user.updated_at,
            )
            for user in self.result
        ]
