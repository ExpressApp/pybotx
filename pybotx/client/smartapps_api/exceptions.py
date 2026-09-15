from pybotx.client.exceptions.base import BaseClientError


class SyncSmartAppEventHandlerNotFoundError(BaseClientError):
    """Handler for synchronous smartapp event not found."""
