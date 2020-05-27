"""Definition of Starlette application that is mock for BotX API."""

from typing import Any, Dict, List, Sequence, Tuple, Type

from starlette.applications import Starlette
from starlette.middleware.base import RequestResponseEndpoint
from starlette.routing import Route

from botx.clients.methods.base import BotXMethod
from botx.testing.botx_mock.asgi.errors import ErrorMiddleware
from botx.testing.botx_mock.asgi.routes.bots import get_token
from botx.testing.botx_mock.asgi.routes.chats import (
    get_info,
    post_add_user,
    post_create,
    post_remove_user,
    post_stealth_disable,
    post_stealth_set,
)
from botx.testing.botx_mock.asgi.routes.command import post_command_result
from botx.testing.botx_mock.asgi.routes.events import post_edit_event
from botx.testing.botx_mock.asgi.routes.notification import (
    post_notification,
    post_notification_direct,
)
from botx.testing.botx_mock.asgi.routes.users import (
    get_by_email,
    get_by_huid,
    get_by_login,
)
from botx.testing.typing import APIMessage, APIRequest

_ENDPOINTS: Tuple[RequestResponseEndpoint, ...] = (
    # V2
    # bots
    get_token,
    # V3
    # chats
    get_info,
    post_add_user,
    post_remove_user,
    post_stealth_set,
    post_stealth_disable,
    post_create,
    # command
    post_command_result,
    # events
    post_edit_event,
    # notification
    post_notification,
    post_notification_direct,
    # users
    get_by_huid,
    get_by_email,
    get_by_login,
)


def _create_starlette_routes() -> Sequence[Route]:
    routes = []

    for endpoint in _ENDPOINTS:
        routes.append(
            Route(
                endpoint.method.__url__,  # type: ignore  WPS609
                endpoint,
                methods=[endpoint.method.__method__],  # type: ignore  WPS609
            ),
        )

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
