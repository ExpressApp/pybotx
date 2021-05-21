import uuid

import pytest

from botx.clients.methods.v3.users.by_huid import ByHUID
from botx.concurrency import callable_to_coroutine

pytestmark = pytest.mark.asyncio
pytest_plugins = ("tests.test_clients.fixtures",)


async def test_search_by_huid(client, requests_client):
    method = ByHUID(host="example.com", user_huid=uuid.uuid4())

    request = requests_client.build_request(method)
    response = await callable_to_coroutine(requests_client.execute, request)
    user = await callable_to_coroutine(
        requests_client.process_response,
        method,
        response,
    )

    assert user.user_huid == method.user_huid

    assert client.requests[0].user_huid == method.user_huid
