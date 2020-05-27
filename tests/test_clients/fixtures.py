import pytest

from botx import AsyncClient, Client


@pytest.fixture(params=(AsyncClient, Client))
def requests_client(request, client):
    if issubclass(request.param, AsyncClient):
        return client.bot.client

    return client.bot.sync_client
