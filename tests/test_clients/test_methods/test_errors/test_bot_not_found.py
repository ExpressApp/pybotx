import uuid
from http import HTTPStatus

import pytest

from botx.clients.methods.errors.bot_not_found import BotNotFoundError
from botx.clients.methods.v2.bots.token import Token
from botx.concurrency import callable_to_coroutine

pytestmark = pytest.mark.asyncio
pytest_plugins = ("tests.test_clients.fixtures",)


async def test_raising_bot_not_found_error(client, requests_client):
    method = Token(host="example.com", bot_id=uuid.uuid4(), signature="signature")

    errors_to_raise = {Token: (HTTPStatus.NOT_FOUND, {})}

    with client.error_client(errors=errors_to_raise):
        request = requests_client.build_request(method)
        response = await callable_to_coroutine(requests_client.execute, request)

        with pytest.raises(BotNotFoundError):
            await callable_to_coroutine(
                requests_client.process_response,
                method,
                response,
            )
