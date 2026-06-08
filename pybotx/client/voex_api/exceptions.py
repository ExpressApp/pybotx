from pybotx.client.exceptions.base import BaseClientError


class ConferenceNotFoundError(BaseClientError):
    """Conference with specified call_id not found."""


class CallNotFoundError(BaseClientError):
    """Call with specified call_id not found."""
