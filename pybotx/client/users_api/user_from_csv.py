from uuid import UUID

from pybotx.models.api_base import VerifiedPayloadBaseModel
from pybotx.models.enums import (
    APISyncSourceTypes,
    APIUserKinds,
    convert_sync_source_type_to_domain,
    convert_user_kind_to_domain,
)
from pybotx.models.users import UserFromCSV
from pydantic import Field, field_validator


class BotXAPIUserFromCSVResult(VerifiedPayloadBaseModel):
    huid: UUID = Field(alias="HUID")
    ad_login: str = Field(alias="AD Login")
    ad_domain: str = Field(alias="Domain")
    email: str | None = Field(alias="AD E-mail")
    name: str = Field(alias="Name")
    sync_source: APISyncSourceTypes | str = Field(alias="Sync source")
    active: bool = Field(alias="Active")
    user_kind: APIUserKinds = Field(alias="Kind")
    company: str | None = Field(alias="Company")
    department: str | None = Field(alias="Department")
    position: str | None = Field(alias="Position")
    avatar: str | None = Field(alias="Avatar")
    avatar_preview: str | None = Field(alias="Avatar preview")
    office: str | None = Field(alias="Office")
    manager: str | None = Field(alias="Manager")
    manager_huid: UUID | None = Field(alias="Manager HUID")
    description: str | None = Field(alias="Description")
    phone: str | None = Field(alias="Phone")
    other_phone: str | None = Field(alias="Other phone")
    ip_phone: str | None = Field(alias="IP phone")
    other_ip_phone: str | None = Field(alias="Other IP phone")
    personnel_number: str | None = Field(alias="Personnel number")

    @field_validator(
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
        mode="before",
    )
    @classmethod
    def replace_empty_string_with_none(cls, field_value: str) -> str | None:
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
