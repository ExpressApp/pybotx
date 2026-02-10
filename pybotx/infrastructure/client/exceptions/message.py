from pybotx.infrastructure.client.exceptions.base import BaseClientError


class MessageNotFoundError(BaseClientError):
    """Message not found."""
