import uuid

import httpx
import pytest

from botx.clients.methods.v3.chats.info import Info
from botx.concurrency import callable_to_coroutine
from botx.exceptions import BotXAPIRouteDeprecated

pytestmark = pytest.mark.asyncio
pytest_plugins = ("tests.test_clients.fixtures",)


async def test_raising_route_deprecated_error(client, requests_client):
    method = Info(group_chat_id=uuid.uuid4())
    errors_to_raise = {Info: (httpx.codes.GONE, {})}

    with client.error_client(errors=errors_to_raise):
        method.host = "example.com"
        request = requests_client.build_request(method)
        response = await callable_to_coroutine(requests_client.execute, request)

        with pytest.raises(BotXAPIRouteDeprecated):
            await callable_to_coroutine(
                requests_client.process_response,
                method,
                response,
            )
