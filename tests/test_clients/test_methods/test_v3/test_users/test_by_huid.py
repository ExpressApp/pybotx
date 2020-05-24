import uuid

import pytest

from botx.clients.methods.v3.users.by_huid import ByHUID

pytestmark = pytest.mark.asyncio


async def test_search_by_huid(client):
    method = ByHUID(user_huid=uuid.uuid4())

    user = await method.call(client.bot.client, "example.cts")

    assert user.user_huid == method.user_huid

    assert client.requests[0].user_huid == method.user_huid
