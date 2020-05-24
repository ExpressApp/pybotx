import uuid

import pytest
from httpx import StatusCode

from botx.clients.methods.errors.user_not_found import UserNotFoundError
from botx.clients.methods.v3.users.by_huid import ByHUID

pytestmark = pytest.mark.asyncio


async def test_raising_user_not_found(client):
    method = ByHUID(user_huid=uuid.uuid4())

    errors_to_raise = {ByHUID: (StatusCode.NOT_FOUND, {})}

    with pytest.raises(UserNotFoundError):
        with client.error_client(errors=errors_to_raise):
            await method.call(client.bot.client, "example.cts")
