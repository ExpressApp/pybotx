import pytest

from botx import Client

pytestmark = pytest.mark.asyncio


@pytest.fixture()
def handler_with_dependency(storage):
    def factory(client: Client) -> None:
        storage.client = client

    return factory


async def test_passing_async_client_as_dependency(
    bot, client, incoming_message, handler_with_dependency, storage,
):
    bot.default(handler_with_dependency)
    await client.send_command(incoming_message)
    assert storage.client == bot.sync_client
