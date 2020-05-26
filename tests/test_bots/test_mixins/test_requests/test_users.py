import pytest

from botx import Message
from botx.clients.methods.v3.users.by_email import ByEmail
from botx.clients.methods.v3.users.by_huid import ByHUID
from botx.clients.methods.v3.users.by_login import ByLogin

pytestmark = pytest.mark.asyncio


async def test_search_requires_one_of_params(client, incoming_message):
    message = Message.from_dict(incoming_message.dict(), client.bot)

    with pytest.raises(ValueError):
        await client.bot.search_user(message.credentials)


async def test_search_using_huid_method(client, incoming_message):
    message = Message.from_dict(incoming_message.dict(), client.bot)
    await client.bot.search_user(message.credentials, user_huid=message.user_huid)

    assert isinstance(client.requests[0], ByHUID)


async def test_search_using_email_method(client, incoming_message):
    message = Message.from_dict(incoming_message.dict(), client.bot)
    await client.bot.search_user(message.credentials, email=message.user.email)

    assert isinstance(client.requests[0], ByEmail)


async def test_search_using_ad_method(client, incoming_message):
    message = Message.from_dict(incoming_message.dict(), client.bot)
    await client.bot.search_user(
        message.credentials, ad=(message.user.ad_login, message.user.ad_domain)
    )

    assert isinstance(client.requests[0], ByLogin)
