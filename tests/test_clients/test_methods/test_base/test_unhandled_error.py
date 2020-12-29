import uuid

import pytest

from botx import BotXAPIError, ChatTypes
from botx.clients.methods.errors.bot_is_not_admin import BotIsNotAdminData
from botx.clients.methods.v2.bots.token import Token
from botx.clients.methods.v3.chats.create import Create
from botx.concurrency import callable_to_coroutine

IM_A_TEAPOT = 418  # This status code added in python 3.9

pytestmark = pytest.mark.asyncio
pytest_plugins = ("tests.test_clients.fixtures",)


async def test_raising_base_api_error_if_empty_handlers(client, requests_client):
    method = Token(bot_id=uuid.uuid4(), signature="signature")

    errors_to_raise = {
        Token: (
            IM_A_TEAPOT,
            BotIsNotAdminData(sender=uuid.uuid4(), group_chat_id=uuid.uuid4()),
        ),
    }

    with client.error_client(errors=errors_to_raise):
        method.host = "example.com"
        request = requests_client.build_request(method)
        response = await callable_to_coroutine(requests_client.execute, method, request)

        with pytest.raises(BotXAPIError):
            await callable_to_coroutine(
                requests_client.process_response, method, response,
            )


async def test_raising_base_api_error_if_unhandled(client, requests_client):
    method = Create(
        name="test name", members=[uuid.uuid4()], chat_type=ChatTypes.group_chat,
    )

    method.__errors_handlers__[IM_A_TEAPOT] = []

    errors_to_raise = {
        Create: (
            IM_A_TEAPOT,
            BotIsNotAdminData(sender=uuid.uuid4(), group_chat_id=uuid.uuid4()),
        ),
    }

    with client.error_client(errors=errors_to_raise):
        method.host = "example.com"
        request = requests_client.build_request(method)
        response = await callable_to_coroutine(requests_client.execute, method, request)

        with pytest.raises(BotXAPIError):
            await callable_to_coroutine(
                requests_client.process_response, method, response,
            )
