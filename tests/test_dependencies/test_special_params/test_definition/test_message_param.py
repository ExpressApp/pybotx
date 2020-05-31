import pytest

from botx import Message

pytestmark = pytest.mark.asyncio


@pytest.fixture()
def handler_with_dependency(storage):
    def factory(message: Message) -> None:
        storage.message = message

    return factory


async def test_passing_async_client_as_dependency(
    bot, client, incoming_message, handler_with_dependency, storage,
):
    bot.default(handler_with_dependency)
    await client.send_command(incoming_message)
    assert storage.message.incoming_message == incoming_message
