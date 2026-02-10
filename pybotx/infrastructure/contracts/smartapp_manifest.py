from __future__ import annotations

from uuid import UUID

from pydantic import Field

from pybotx.domain.missing import Missing, Undefined
from pybotx.domain.models.enums import SmartappManifestWebLayoutChoices as WebLayoutChoices
from pybotx.domain.models.smartapp_manifest import (
    SmartappManifest as DomainSmartappManifest,
    SmartappManifestAndroidParams as DomainSmartappManifestAndroidParams,
    SmartappManifestAuroraParams as DomainSmartappManifestAuroraParams,
    SmartappManifestIosParams as DomainSmartappManifestIosParams,
    SmartappManifestUnreadCounterParams as DomainSmartappManifestUnreadCounterParams,
    SmartappManifestWebParams as DomainSmartappManifestWebParams,
)
from pybotx.infrastructure.contracts.api_base import (
    UnverifiedPayloadBaseModel,
    VerifiedPayloadBaseModel,
)


class SmartappManifestIosParams(VerifiedPayloadBaseModel):
    fullscreen_layout: bool = False

    @classmethod
    def from_domain(
        cls,
        params: DomainSmartappManifestIosParams,
    ) -> "SmartappManifestIosParams":
        return cls(fullscreen_layout=params.fullscreen_layout)

    def to_domain(self) -> DomainSmartappManifestIosParams:
        return DomainSmartappManifestIosParams(
            fullscreen_layout=self.fullscreen_layout,
        )


class SmartappManifestAndroidParams(VerifiedPayloadBaseModel):
    fullscreen_layout: bool = False

    @classmethod
    def from_domain(
        cls,
        params: DomainSmartappManifestAndroidParams,
    ) -> "SmartappManifestAndroidParams":
        return cls(fullscreen_layout=params.fullscreen_layout)

    def to_domain(self) -> DomainSmartappManifestAndroidParams:
        return DomainSmartappManifestAndroidParams(
            fullscreen_layout=self.fullscreen_layout,
        )


class SmartappManifestAuroraParams(VerifiedPayloadBaseModel):
    fullscreen_layout: bool = False

    @classmethod
    def from_domain(
        cls,
        params: DomainSmartappManifestAuroraParams,
    ) -> "SmartappManifestAuroraParams":
        return cls(fullscreen_layout=params.fullscreen_layout)

    def to_domain(self) -> DomainSmartappManifestAuroraParams:
        return DomainSmartappManifestAuroraParams(
            fullscreen_layout=self.fullscreen_layout,
        )


class SmartappManifestWebParams(VerifiedPayloadBaseModel):
    default_layout: WebLayoutChoices = WebLayoutChoices.minimal
    expanded_layout: WebLayoutChoices = WebLayoutChoices.half
    allowed_layouts: list[WebLayoutChoices] | None = None
    always_pinned: bool = False

    @classmethod
    def from_domain(
        cls,
        params: DomainSmartappManifestWebParams,
    ) -> "SmartappManifestWebParams":
        return cls(
            default_layout=params.default_layout,
            expanded_layout=params.expanded_layout,
            allowed_layouts=params.allowed_layouts,
            always_pinned=params.always_pinned,
        )

    def to_domain(self) -> DomainSmartappManifestWebParams:
        return DomainSmartappManifestWebParams(
            default_layout=self.default_layout,
            expanded_layout=self.expanded_layout,
            allowed_layouts=self.allowed_layouts,
            always_pinned=self.always_pinned,
        )


class SmartappManifestUnreadCounterParams(VerifiedPayloadBaseModel):
    user_huid: list[UUID] = Field(default_factory=list)
    group_chat_id: list[UUID] = Field(default_factory=list)
    app_id: list[str] = Field(default_factory=list)

    @classmethod
    def from_domain(
        cls,
        params: DomainSmartappManifestUnreadCounterParams,
    ) -> "SmartappManifestUnreadCounterParams":
        return cls(
            user_huid=params.user_huid,
            group_chat_id=params.group_chat_id,
            app_id=params.app_id,
        )

    def to_domain(self) -> DomainSmartappManifestUnreadCounterParams:
        return DomainSmartappManifestUnreadCounterParams(
            user_huid=self.user_huid,
            group_chat_id=self.group_chat_id,
            app_id=self.app_id,
        )


class SmartappManifest(VerifiedPayloadBaseModel):
    ios: SmartappManifestIosParams
    android: SmartappManifestAndroidParams
    web: SmartappManifestWebParams
    unread_counter_link: SmartappManifestUnreadCounterParams

    @classmethod
    def from_domain(
        cls,
        manifest: DomainSmartappManifest,
    ) -> "SmartappManifest":
        return cls(
            ios=SmartappManifestIosParams.from_domain(manifest.ios),
            android=SmartappManifestAndroidParams.from_domain(manifest.android),
            web=SmartappManifestWebParams.from_domain(manifest.web),
            unread_counter_link=SmartappManifestUnreadCounterParams.from_domain(
                manifest.unread_counter_link
            ),
        )

    def to_domain(self) -> DomainSmartappManifest:
        return DomainSmartappManifest(
            ios=self.ios.to_domain(),
            android=self.android.to_domain(),
            web=self.web.to_domain(),
            unread_counter_link=self.unread_counter_link.to_domain(),
        )


class SmartappManifestPayload(UnverifiedPayloadBaseModel):
    ios: Missing[SmartappManifestIosParams] = Undefined
    android: Missing[SmartappManifestAndroidParams] = Undefined
    web: Missing[SmartappManifestWebParams] = Undefined
    aurora: Missing[SmartappManifestAuroraParams] = Undefined
    unread_counter_link: Missing[SmartappManifestUnreadCounterParams] = Undefined


__all__ = (
    "SmartappManifest",
    "SmartappManifestAndroidParams",
    "SmartappManifestAuroraParams",
    "SmartappManifestIosParams",
    "SmartappManifestPayload",
    "SmartappManifestUnreadCounterParams",
    "SmartappManifestWebParams",
)
