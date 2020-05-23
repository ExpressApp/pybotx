import pytest

from botx.clients.methods.v3.users.by_email import ByEmail

pytestmark = pytest.mark.asyncio


async def test_search_by_huid(client):
    method = ByEmail(email="test@example.com")
    method.fill_credentials("example.cts", "")

    user = await method.call(client.bot.client)

    assert user.emails == [method.email]

    assert client.requests[0].email == method.email
