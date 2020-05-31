"""Logic for extending messages and requests collections from test client."""

from molten import Settings

from botx.clients.methods.base import BotXMethod


def add_message_to_collection(settings: Settings, message: BotXMethod) -> None:
    """Add new message to messages collection.

    Arguments:
        settings: application settings with storage.
        message: message that should be added.
    """
    messages = settings["messages"]
    messages.append(message)
    add_request_to_collection(settings, message)


def add_request_to_collection(settings: Settings, api_request: BotXMethod) -> None:
    """Add new API request to requests collection.

    Arguments:
        settings: application settings with storage.
        api_request: API request that should be added.
    """
    requests = settings["requests"]
    requests.append(api_request)
