import uuid
from http import HTTPStatus

import pytest

from botx.clients.methods.errors.user_not_found import UserNotFoundError
from botx.clients.methods.v3.users.by_huid import ByHUID
from botx.concurrency import callable_to_coroutine

pytestmark = pytest.mark.asyncio
pytest_plugins = ("tests.test_clients.fixtures",)


async def test_raising_user_not_found(client, requests_client):
    method = ByHUID(host="example.com", user_huid=uuid.uuid4())

    errors_to_raise = {ByHUID: (HTTPStatus.NOT_FOUND, {})}

    with client.error_client(errors=errors_to_raise):
        request = requests_client.build_request(method)
        response = await callable_to_coroutine(requests_client.execute, request)

        with pytest.raises(UserNotFoundError):
            await callable_to_coroutine(
                requests_client.process_response,
                method,
                response,
            )
