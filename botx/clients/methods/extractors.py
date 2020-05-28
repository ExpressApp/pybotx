"""Custom extractors for responses from BotX API."""
from uuid import UUID

from botx.clients.methods.base import BotXMethod
from botx.clients.types.response_results import ChatCreatedResult, PushResult


def extract_generated_sync_id(_method: BotXMethod, push: PushResult) -> UUID:
    """Extract generated sync ID from response.

    Arguments:
        _method: method that was used for making request.
        push: push response from BotX API for generated message.

    Returns:
        Extracted sync ID.
    """
    return push.sync_id


def extract_generated_chat_id(_method: BotXMethod, response: ChatCreatedResult) -> UUID:
    """Extract generated sync ID from response.

    Arguments:
        _method: method that was used for making request.
        response: response for created chat.

    Returns:
        Extracted chat ID.
    """
    return response.chat_id
