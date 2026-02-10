from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID

from pybotx.domain.models.enums import SmartappManifestWebLayoutChoices as WebLayoutChoices


@dataclass(slots=True)
class SmartappManifestIosParams:
    fullscreen_layout: bool = False


@dataclass(slots=True)
class SmartappManifestAndroidParams:
    fullscreen_layout: bool = False


@dataclass(slots=True)
class SmartappManifestAuroraParams:
    fullscreen_layout: bool = False


@dataclass(slots=True)
class SmartappManifestWebParams:
    default_layout: WebLayoutChoices = WebLayoutChoices.minimal
    expanded_layout: WebLayoutChoices = WebLayoutChoices.half
    allowed_layouts: list[WebLayoutChoices] | None = None
    always_pinned: bool = False


@dataclass(slots=True)
class SmartappManifestUnreadCounterParams:
    user_huid: list[UUID] = field(default_factory=list)
    group_chat_id: list[UUID] = field(default_factory=list)
    app_id: list[str] = field(default_factory=list)


@dataclass(slots=True)
class SmartappManifest:
    ios: SmartappManifestIosParams
    android: SmartappManifestAndroidParams
    web: SmartappManifestWebParams
    unread_counter_link: SmartappManifestUnreadCounterParams


__all__ = (
    "SmartappManifest",
    "SmartappManifestAndroidParams",
    "SmartappManifestAuroraParams",
    "SmartappManifestIosParams",
    "SmartappManifestUnreadCounterParams",
    "SmartappManifestWebParams",
)
