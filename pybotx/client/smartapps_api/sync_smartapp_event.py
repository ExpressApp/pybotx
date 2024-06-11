from pybotx.client.smartapps_api.smartapp_event import (
    BotXAPISmartAppEventRequestPayload,
)


class SyncSmartAppEventResponsePayload(BotXAPISmartAppEventRequestPayload):
    """The response payload to a synchronous smartapp event at /smartapps/request."""
