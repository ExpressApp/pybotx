from pybotx.client.exceptions.base import BaseClientError


class SyncSmartAppRequestHandlerNotFoundError(BaseClientError):
    """Handler for synchronous smartapp request not found."""
