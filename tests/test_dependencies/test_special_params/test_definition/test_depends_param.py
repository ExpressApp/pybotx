import pytest

from botx import Depends

pytestmark = pytest.mark.asyncio


def dependency():
    return 42


@pytest.fixture()
def handler_with_dependency(storage):
    def factory(dep: int = Depends(dependency)) -> None:
        storage.dep = dep

    return factory


async def test_passing_async_client_as_dependency(
    bot, client, incoming_message, handler_with_dependency, storage
):
    bot.default(handler_with_dependency)
    await client.send_command(incoming_message)
    assert storage.dep == 42
