from typing import Optional, Union
from uuid import UUID

from pydantic import Field, validator

from pybotx.models.api_base import VerifiedPayloadBaseModel
from pybotx.models.enums import (
    APISyncSourceTypes,
    APIUserKinds,
    convert_sync_source_type_to_domain,
    convert_user_kind_to_domain,
)
from pybotx.models.users import UserFromCSV


class BotXAPIUserFromCSVResult(VerifiedPayloadBaseModel):
    huid: UUID = Field(alias="HUID")
    ad_login: str = Field(alias="AD Login")
    ad_domain: str = Field(alias="Domain")
    email: Optional[str] = Field(alias="AD E-mail")
    name: str = Field(alias="Name")
    sync_source: Union[APISyncSourceTypes, str] = Field(alias="Sync source")
    active: bool = Field(alias="Active")
    user_kind: APIUserKinds = Field(alias="Kind")
    company: Optional[str] = Field(alias="Company")
    department: Optional[str] = Field(alias="Department")
    position: Optional[str] = Field(alias="Position")
    avatar: Optional[str] = Field(alias="Avatar")
    avatar_preview: Optional[str] = Field(alias="Avatar preview")
    office: Optional[str] = Field(alias="Office")
    manager: Optional[str] = Field(alias="Manager")
    manager_huid: Optional[UUID] = Field(alias="Manager HUID")
    description: Optional[str] = Field(alias="Description")
    phone: Optional[str] = Field(alias="Phone")
    other_phone: Optional[str] = Field(alias="Other phone")
    ip_phone: Optional[str] = Field(alias="IP phone")
    other_ip_phone: Optional[str] = Field(alias="Other IP phone")
    personnel_number: Optional[str] = Field(alias="Personnel number")

    @validator(
        "email",
        "company",
        "department",
        "position",
        "avatar",
        "avatar_preview",
        "office",
        "manager",
        "manager_huid",
        "description",
        "phone",
        "other_phone",
        "ip_phone",
        "other_ip_phone",
        "personnel_number",
        pre=True,
    )
    @classmethod
    def replace_empty_string_with_none(cls, field_value: str) -> Optional[str]:
        if field_value == "":
            return None

        return field_value

    def to_domain(self) -> UserFromCSV:
        return UserFromCSV(
            huid=self.huid,
            ad_login=self.ad_login,
            ad_domain=self.ad_domain,
            email=self.email,
            username=self.name,
            sync_source=convert_sync_source_type_to_domain(self.sync_source),
            active=self.active,
            user_kind=convert_user_kind_to_domain(self.user_kind),
            company=self.company,
            department=self.department,
            position=self.position,
            avatar=self.avatar,
            avatar_preview=self.avatar_preview,
            office=self.office,
            manager=self.manager,
            manager_huid=self.manager_huid,
            description=self.description,
            phone=self.phone,
            other_phone=self.other_phone,
            ip_phone=self.ip_phone,
            other_ip_phone=self.other_ip_phone,
            personnel_number=self.personnel_number,
        )
