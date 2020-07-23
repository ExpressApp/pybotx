import pytest

from botx.clients.methods.v3.users.by_email import ByEmail
from botx.concurrency import callable_to_coroutine

pytestmark = pytest.mark.asyncio
pytest_plugins = ("tests.test_clients.fixtures",)


async def test_search_by_huid(client, requests_client):
    method = ByEmail(email="test@example.com")

    user = await callable_to_coroutine(requests_client.call, method, "example.cts")

    assert user.emails == [method.email]

    assert client.requests[0].email == method.email
