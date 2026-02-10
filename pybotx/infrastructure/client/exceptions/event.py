from pybotx.infrastructure.client.exceptions.base import BaseClientError


class EventNotFoundError(BaseClientError):
    """Event not found."""
