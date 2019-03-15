import pytest

from botx import CommandHandler, BotXException
from botx.core.dispatcher import SyncDispatcher, AsyncDispatcher


def test_dispatcher_create_status():
    d = SyncDispatcher(4)
    d.add_handler(
        CommandHandler(
            name="name",
            command="/command",
            description="description",
            func=lambda m: None,
        )
    )
    assert d._create_status().dict() == {
        "status": "ok",
        "result": {
            "enabled": True,
            "status_message": "Bot is working",
            "commands": [
                {
                    "body": "/command",
                    "description": "description",
                    "elements": [],
                    "name": "name",
                    "options": {},
                }
            ],
        },
    }


def test_sync_dispatcher_parse_request(test_command_data):
    d = SyncDispatcher(4)
    with pytest.raises(BotXException):
        d.parse_request({}, request_type="error")
    assert d.parse_request({}, request_type="status") == {
        "status": "ok",
        "result": {"enabled": True, "status_message": "Bot is working", "commands": []},
    }
    assert not d.parse_request(test_command_data, request_type="command")
    d.add_handler(
        CommandHandler(
            name="name",
            command="/command",
            description="description",
            func=lambda m: m,
            use_as_default_handler=True,
        )
    )
    assert d.parse_request(test_command_data, request_type="command")
    with pytest.raises(BotXException):

        async def f():
            pass

        d.add_handler(
            CommandHandler(
                name="name",
                command="/command",
                description="description",
                func=f,
                use_as_default_handler=True,
            )
        )


@pytest.mark.asyncio
async def test_async_dispatcher(test_command_data):
    d = AsyncDispatcher()
    await d.start()

    assert await d.parse_request({}, request_type="status") == {
        "status": "ok",
        "result": {"enabled": True, "status_message": "Bot is working", "commands": []},
    }
    assert not await d.parse_request(test_command_data, request_type="command")

    async def f(m):
        pass

    d.add_handler(
        CommandHandler(
            name="name",
            command="/command",
            description="description",
            func=f,
            use_as_default_handler=True,
        )
    )
    assert await d.parse_request(test_command_data, request_type="command")

    d.add_handler(
        CommandHandler(name="name", command="/cmd", description="description", func=f)
    )
    assert await d.parse_request(test_command_data, request_type="command")

    with pytest.raises(BotXException):
        d.add_handler(CommandHandler(name='', command='', description='', func=lambda m: m))

    await d.shutdown()
