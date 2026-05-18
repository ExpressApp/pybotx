from typing import Any

import pytest

from pybotx.models.enums import ClientNetworkContours
from pybotx.models.sync_smartapp_event import BotAPISyncSmartAppEvent


@pytest.mark.parametrize(
    ("api_value", "domain_value"),
    [
        ("internal", ClientNetworkContours.INTERNAL),
        ("external", ClientNetworkContours.EXTERNAL),
    ],
)
def test__sync_smartapp_event__client_network_contour_mapped_to_sender(
    api_value: str,
    domain_value: ClientNetworkContours,
) -> None:
    payload = _sync_smartapp_event_payload(client_network_contour=api_value)

    event = BotAPISyncSmartAppEvent.model_validate(payload).to_domain(payload)

    assert event.sender.client_network_contour == domain_value


def _sync_smartapp_event_payload(
    *,
    client_network_contour: str,
) -> dict[str, Any]:
    return {
        "bot_id": "2a98219d-1f57-5dcb-920c-9a992bde01ec",
        "group_chat_id": "1ee7fdcf-e258-03d6-2263-2764da127088",
        "method": "menu",
        "payload": {
            "data": {
                "camelCaseValue": "value2",
                "under_score_value": "value1",
            },
            "files": [],
            "opts": {},
        },
        "sender_info": {
            "client_network_contour": client_network_contour,
            "platform": "web",
            "udid": "9eb0ed48-2501-59b8-9ba1-9136ff6efc59",
            "user_huid": "347fdc52-fd0f-5e1d-b06f-bdfdf1cc7164",
        },
    }
