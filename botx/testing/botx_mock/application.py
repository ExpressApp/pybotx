"""Definition of Starlette application that is mock for BotX API."""

from types import MappingProxyType
from typing import List, Mapping, Sequence

from starlette.applications import Starlette
from starlette.middleware.base import RequestResponseEndpoint
from starlette.routing import Route

from botx.api_helpers import BotXAPI, BotXEndpoint
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
from botx.testing.botx_mock.routes.notification import post_notification_direct
from botx.testing.typing import APIMessage, APIRequest

_ENDPOINT_TO_IMPLEMENTATION: Mapping[
    BotXEndpoint, RequestResponseEndpoint
] = MappingProxyType(
    {
        BotXAPI.token_endpoint: get_token,
        BotXAPI.command_endpoint: post_command_result,
        BotXAPI.direct_notification_endpoint: post_notification_direct,
        BotXAPI.edit_event_endpoint: post_edit_event,
        BotXAPI.add_user_endpoint: post_add_user,
        BotXAPI.remove_user_endpoint: post_remove_user,
        BotXAPI.stealth_set_endpoint: post_stealth_set,
        BotXAPI.stealth_disable_endpoint: post_stealth_disable,
    }
)


def _create_starlette_routes() -> Sequence[Route]:
    routes = []

    for endpoint, implementation in _ENDPOINT_TO_IMPLEMENTATION.items():
        routes.append(
            Route(endpoint.endpoint, implementation, methods=[endpoint.method])
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
