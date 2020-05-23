import pytest

from botx.clients.methods.v3.users.by_login import ByLogin

pytestmark = pytest.mark.asyncio


async def test_search_by_huid(client):
    method = ByLogin(ad_login="test", ad_domain="example.com")
    method.fill_credentials("example.cts", "")

    user = await method.call(client.bot.client)

    assert user.ad_login == method.ad_login
    assert user.ad_domain == method.ad_domain

    assert client.requests[0].ad_login == method.ad_login
    assert client.requests[0].ad_domain == method.ad_domain
