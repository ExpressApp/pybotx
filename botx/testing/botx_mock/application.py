"""Definition of Starlette application that is mock for BotX API."""

from typing import List, Sequence, Tuple

from starlette.applications import Starlette
from starlette.middleware.base import RequestResponseEndpoint
from starlette.routing import Route

from botx.testing.botx_mock.errors import ErrorMiddleware
from botx.testing.botx_mock.routes.bots import get_token
from botx.testing.botx_mock.routes.chats import (
    post_add_user,
    post_remove_user,
    post_stealth_disable,
    post_stealth_set,
)
from botx.testing.botx_mock.routes.command import post_command_result
from botx.testing.botx_mock.routes.events import post_edit_event
from botx.testing.botx_mock.routes.notification import (
    post_notification,
    post_notification_direct,
)
from botx.testing.typing import APIMessage, APIRequest

_ENDPOINTS: Tuple[RequestResponseEndpoint, ...] = (
    get_token,
    post_add_user,
    post_remove_user,
    post_stealth_set,
    post_stealth_disable,
    post_command_result,
    post_edit_event,
    post_notification,
    post_notification_direct,
)


def _create_starlette_routes() -> Sequence[Route]:
    routes = []

    for endpoint in _ENDPOINTS:
        routes.append(
            Route(
                endpoint.method.__url__,  # noqa: WPS609
                endpoint,
                methods=[endpoint.method.__method__],  # noqa: WPS609
            )
        )

    return routes


def get_botx_api(
    messages: List[APIMessage],
    requests: List[APIRequest],
    generate_errors: bool = False,
) -> Starlette:
    """Generate BotX API mock.

    Arguments:
        messages: list of message that were sent from bot and should be extended.
        requests: all requests that were sent from bot.
        generate_errors: should API generate errored responses.

    Returns:
        Generated BotX API mock for using with httpx.
    """
    botx_app = Starlette(routes=list(_create_starlette_routes()))
    botx_app.add_middleware(ErrorMiddleware)
    botx_app.state.messages = messages
    botx_app.state.requests = requests
    botx_app.state.generate_errors = generate_errors

    return botx_app
