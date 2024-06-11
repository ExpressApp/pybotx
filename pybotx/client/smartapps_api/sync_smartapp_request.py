from pybotx.client.smartapps_api.smartapp_event import (
    BotXAPISmartAppEventRequestPayload,
)


class SyncSmartAppRequestResponsePayload(BotXAPISmartAppEventRequestPayload):
    """The response payload to a synchronous smartapp request at /smartapps/request."""
