import uuid

import pytest
from httpx import StatusCode

from botx import BotXAPIError, ChatTypes
from botx.clients.methods.errors.bot_is_not_admin import BotIsNotAdminData
from botx.clients.methods.v2.bots.token import Token
from botx.clients.methods.v3.chats.create import Create

pytestmark = pytest.mark.asyncio


async def test_raising_base_api_error_if_empty_handlers(client):
    method = Token(bot_id=uuid.uuid4(), signature="signature")
    method.fill_credentials("example.cts", "")

    errors_to_raise = {
        Token: (
            StatusCode.IM_A_TEAPOT,
            BotIsNotAdminData(sender=uuid.uuid4(), group_chat_id=uuid.uuid4()),
        )
    }

    with pytest.raises(BotXAPIError):
        with client.error_client(errors=errors_to_raise):
            await method.call(client.bot.client)


async def test_raising_base_api_error_if_unhandled(client):
    method = Create(
        name="test name", members=[uuid.uuid4()], chat_type=ChatTypes.group_chat
    )
    method.fill_credentials("example.cts", "")

    method.__errors_handlers__[StatusCode.IM_A_TEAPOT] = []

    errors_to_raise = {
        Create: (
            StatusCode.IM_A_TEAPOT,
            BotIsNotAdminData(sender=uuid.uuid4(), group_chat_id=uuid.uuid4()),
        )
    }

    with pytest.raises(BotXAPIError):
        with client.error_client(errors=errors_to_raise):
            await method.call(client.bot.client)
