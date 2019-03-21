import pytest

from botx import BotXException, CommandHandler, RequestTypeEnum, Status, StatusResult
from botx.bot.dispatcher.asyncdispatcher import AsyncDispatcher


@pytest.mark.asyncio
async def test_async_dispatcher_init():
    d = AsyncDispatcher(None)
    await d.start()
    assert d._scheduler is not None
    await d.shutdown()


@pytest.mark.asyncio
async def test_sync_dispatcher_wrong_request_parsing():
    d = AsyncDispatcher(None)
    await d.start()
    with pytest.raises(BotXException):
        await d.parse_request({}, request_type="wrong type")
    await d.shutdown()


@pytest.mark.asyncio
async def test_sync_dispatcher_command_request_parsing(command_with_text_and_file):
    d = AsyncDispatcher(None)
    await d.start()
    r = await d.parse_request(command_with_text_and_file, RequestTypeEnum.command)
    assert not r
    await d.shutdown()


@pytest.mark.asyncio
async def test_sync_dispatcher_status_creation(custom_async_handler):
    d = AsyncDispatcher(None)
    await d.start()
    d.add_handler(custom_async_handler)
    assert await d.parse_request({}, request_type="status") == Status(
        result=StatusResult(commands=[custom_async_handler.to_status_command()])
    )
    await d.shutdown()


@pytest.mark.asyncio
async def test_sync_dispatcher_default_handler_processing(command_with_text_and_file):
    d = AsyncDispatcher(None)
    await d.start()

    result_array = []

    async def handler_function(message, bot):
        result_array.append("default")

    d.add_handler(
        CommandHandler(
            command="/cmd",
            name="handler",
            description="description",
            func=handler_function,
            use_as_default_handler=True,
        )
    )

    await d.parse_request(command_with_text_and_file, request_type="command")

    await d.shutdown()

    assert len(result_array) == 1
    assert result_array[0] == "default"


@pytest.mark.asyncio
async def test_sync_dispatcher_message_creation(command_with_text_and_file):
    d = AsyncDispatcher(None)
    await d.start()
    result_array = []

    async def handler_function(message, bot):
        result_array.append(message.body)

    d.add_handler(
        CommandHandler(
            command="/cmd",
            name="handler",
            description="description",
            func=handler_function,
        )
    )

    for _ in range(3):
        await d.parse_request(command_with_text_and_file, request_type="command")

    await d.shutdown()

    assert len(result_array) == 3
    for r in result_array:
        assert r == "/cmd arg"


@pytest.mark.asyncio
async def test_sync_dispatcher_not_accepting_coroutine_as_handler():
    d = AsyncDispatcher(None)
    await d.start()

    def f(m):
        pass

    with pytest.raises(BotXException):
        d.add_handler(CommandHandler(name="a", command="a", description="a", func=f))

    await d.shutdown()
