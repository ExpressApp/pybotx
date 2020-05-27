import pytest

from botx.clients.methods.v3.users.by_login import ByLogin
from botx.concurrency import callable_to_coroutine

pytestmark = pytest.mark.asyncio
pytest_plugins = ("tests.test_clients.fixtures",)


async def test_search_by_huid(client, requests_client):
    method = ByLogin(ad_login="test", ad_domain="example.com")

    user = await callable_to_coroutine(requests_client.call, method, "example.cts")

    assert user.ad_login == method.ad_login
    assert user.ad_domain == method.ad_domain

    assert client.requests[0].ad_login == method.ad_login
    assert client.requests[0].ad_domain == method.ad_domain
