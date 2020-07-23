import uuid

import pytest

from botx.clients.methods.v3.users.by_huid import ByHUID
from botx.concurrency import callable_to_coroutine

pytestmark = pytest.mark.asyncio
pytest_plugins = ("tests.test_clients.fixtures",)


async def test_search_by_huid(client, requests_client):
    method = ByHUID(user_huid=uuid.uuid4())

    user = await callable_to_coroutine(requests_client.call, method, "example.cts")

    assert user.user_huid == method.user_huid

    assert client.requests[0].user_huid == method.user_huid
