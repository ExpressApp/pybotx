from uuid import UUID

from pybotx.domain.models.enums import SmartappManifestWebLayoutChoices
from pybotx.domain.models.smartapp_manifest import (
    SmartappManifest as DomainSmartappManifest,
    SmartappManifestAndroidParams,
    SmartappManifestAuroraParams as DomainSmartappManifestAuroraParams,
    SmartappManifestIosParams,
    SmartappManifestUnreadCounterParams,
    SmartappManifestWebParams,
)
from pybotx.infrastructure.contracts.smartapp_manifest import (
    SmartappManifest,
    SmartappManifestAuroraParams,
)


def test__smartapp_manifest__roundtrip() -> None:
    domain = DomainSmartappManifest(
        ios=SmartappManifestIosParams(fullscreen_layout=True),
        android=SmartappManifestAndroidParams(fullscreen_layout=False),
        web=SmartappManifestWebParams(
            default_layout=SmartappManifestWebLayoutChoices.half,
            expanded_layout=SmartappManifestWebLayoutChoices.full,
            allowed_layouts=[SmartappManifestWebLayoutChoices.full],
            always_pinned=True,
        ),
        unread_counter_link=SmartappManifestUnreadCounterParams(
            user_huid=[UUID("24348246-6791-4ac0-9d86-b948cd6a0e46")],
            group_chat_id=[UUID("2d40f656-bd40-4b62-9c96-3a6bed22a1dd")],
            app_id=["app"],
        ),
    )

    api = SmartappManifest.from_domain(domain)
    assert api.web.default_layout == SmartappManifestWebLayoutChoices.half

    restored = api.to_domain()
    assert restored == domain


def test__smartapp_manifest__aurora_params_roundtrip() -> None:
    domain = DomainSmartappManifestAuroraParams(fullscreen_layout=True)
    api = SmartappManifestAuroraParams.from_domain(domain)

    assert api.fullscreen_layout is True
    assert api.to_domain() == domain
