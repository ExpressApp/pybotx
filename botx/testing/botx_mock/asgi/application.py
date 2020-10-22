"""Definition of Starlette application that is mock for BotX API."""

from typing import Any, Dict, List, Sequence, Tuple, Type

from starlette.applications import Starlette
from starlette.middleware.base import RequestResponseEndpoint
from starlette.routing import Route

from botx.clients.methods.base import BotXMethod
from botx.testing.botx_mock.asgi.errors import ErrorMiddleware
from botx.testing.botx_mock.asgi.routes import (
    bots,
    chats,
    command,
    events,
    notification,
    users,
)
from botx.testing.typing import APIMessage, APIRequest

_ENDPOINTS: Tuple[RequestResponseEndpoint, ...] = (
    # V2
    # bots
    bots.get_token,
    # V3
    # chats
    chats.get_info,
    chats.post_add_admin_role,
    chats.post_add_user,
    chats.post_remove_user,
    chats.post_stealth_set,
    chats.post_stealth_disable,
    chats.post_create,
    # command
    command.post_command_result,
    # events
    events.post_edit_event,
    # notification
    notification.post_notification,
    notification.post_notification_direct,
    # users
    users.get_by_huid,
    users.get_by_email,
    users.get_by_login,
)


def _create_starlette_routes() -> Sequence[Route]:
    routes = []

    for endpoint in _ENDPOINTS:
        url = endpoint.method.__url__  # type: ignore  # noqa: WPS609
        method = endpoint.method.__method__  # type: ignore  # noqa: WPS609
        routes.append(Route(url, endpoint, methods=[method]))

    return routes


def get_botx_asgi_api(
    messages: List[APIMessage],
    requests: List[APIRequest],
    errors: Dict[Type[BotXMethod], Tuple[int, Any]],
) -> Starlette:
    """Generate BotX API mock.

    Arguments:
        messages: list of message that were sent from bot and should be extended.
        requests: all requests that were sent from bot.
        errors: errors to be generated by mocked API.

    Returns:
        Generated BotX API mock for using with httpx.
    """
    botx_app = Starlette(routes=list(_create_starlette_routes()))
    botx_app.add_middleware(ErrorMiddleware)
    botx_app.state.messages = messages
    botx_app.state.requests = requests
    botx_app.state.errors = errors

    return botx_app
