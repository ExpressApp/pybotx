import uuid

import pytest
from httpx import StatusCode

from botx.clients.methods.errors.user_not_found import UserNotFoundError
from botx.clients.methods.v3.users.by_huid import ByHUID
from botx.concurrency import callable_to_coroutine

pytestmark = pytest.mark.asyncio
pytest_plugins = ("tests.test_clients.fixtures",)


async def test_raising_user_not_found(client, requests_client):
    method = ByHUID(user_huid=uuid.uuid4())

    errors_to_raise = {ByHUID: (StatusCode.NOT_FOUND, {})}

    with pytest.raises(UserNotFoundError):
        with client.error_client(errors=errors_to_raise):
            await callable_to_coroutine(requests_client.call, method, "example.cts")
