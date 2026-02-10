from uuid import UUID

from pybotx.domain.missing import Undefined
from pybotx.domain.models.enums import SmartappManifestWebLayoutChoices
from pybotx.domain.models.smartapp_manifest import (
    SmartappManifestAndroidParams,
    SmartappManifestIosParams,
    SmartappManifestUnreadCounterParams,
    SmartappManifestWebParams,
)
from pybotx.infrastructure.client.smartapps_api.smartapp_manifest import (
    BotXAPISmartAppManifestRequestPayload,
)


def test__smartapp_manifest_request_payload__empty() -> None:
    payload = BotXAPISmartAppManifestRequestPayload.from_domain()

    assert payload.manifest == {}


def test__smartapp_manifest_request_payload__full() -> None:
    ios = SmartappManifestIosParams(fullscreen_layout=True)
    android = SmartappManifestAndroidParams(fullscreen_layout=True)
    web = SmartappManifestWebParams(
        default_layout=SmartappManifestWebLayoutChoices.half,
        expanded_layout=SmartappManifestWebLayoutChoices.full,
        allowed_layouts=[SmartappManifestWebLayoutChoices.full],
        always_pinned=True,
    )
    unread = SmartappManifestUnreadCounterParams(
        user_huid=[UUID("24348246-6791-4ac0-9d86-b948cd6a0e46")],
        group_chat_id=[UUID("2d40f656-bd40-4b62-9c96-3a6bed22a1dd")],
        app_id=["app"],
    )

    payload = BotXAPISmartAppManifestRequestPayload.from_domain(
        ios=ios,
        android=android,
        web_layout=web,
        unread_counter=unread,
    )

    assert payload.manifest.ios.fullscreen_layout is True
    assert payload.manifest.android.fullscreen_layout is True
    assert payload.manifest.web.default_layout == SmartappManifestWebLayoutChoices.half
    assert payload.manifest.unread_counter_link.user_huid == unread.user_huid


def test__smartapp_manifest_request_payload__web_only() -> None:
    web = SmartappManifestWebParams(
        default_layout=SmartappManifestWebLayoutChoices.half,
        expanded_layout=SmartappManifestWebLayoutChoices.full,
        allowed_layouts=[SmartappManifestWebLayoutChoices.full],
        always_pinned=False,
    )

    payload = BotXAPISmartAppManifestRequestPayload.from_domain(
        web_layout=web,
    )

    assert payload.manifest.web.default_layout == SmartappManifestWebLayoutChoices.half
    assert payload.manifest.ios is Undefined
    assert payload.manifest.android is Undefined
    assert payload.manifest.unread_counter_link is Undefined


def test__smartapp_manifest_request_payload__unread_only() -> None:
    unread = SmartappManifestUnreadCounterParams(
        user_huid=[UUID("24348246-6791-4ac0-9d86-b948cd6a0e46")],
        group_chat_id=[UUID("2d40f656-bd40-4b62-9c96-3a6bed22a1dd")],
        app_id=["app"],
    )

    payload = BotXAPISmartAppManifestRequestPayload.from_domain(
        unread_counter=unread,
    )

    assert payload.manifest.unread_counter_link.user_huid == unread.user_huid
    assert payload.manifest.ios is Undefined
    assert payload.manifest.android is Undefined
    assert payload.manifest.web is Undefined
