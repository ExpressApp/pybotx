import uuid

from botx import Bot, Message


def test_command_decorator():
    bot = Bot()
    bot.start()

    assert bot._workers == 4 and bot._dispatcher._pool._max_workers == 4

    @bot.command
    def cmd_handler(message: Message):
        pass

    assert len(bot._dispatcher._handlers) == 1
    handler = bot._dispatcher._handlers.get("/cmdhandler")
    assert handler is not None
    assert handler.name == "Cmdhandler"
    assert handler.command == "/cmdhandler"
    assert handler.description == "cmdhandler command"

    @bot.command
    def cmd_command(message: Message):
        pass

    assert len(bot._dispatcher._handlers) == 2
    handler = bot._dispatcher._handlers.get("/cmd")
    assert handler is not None
    assert handler.name == "Cmd"
    assert handler.command == "/cmd"
    assert handler.description == "cmd command"

    @bot.command()
    def cmd_handler(message: Message):
        pass

    assert len(bot._dispatcher._handlers) == 2
    handler = bot._dispatcher._handlers.get("/cmdhandler")
    assert handler is not None
    assert handler.name == "Cmdhandler"
    assert handler.command == "/cmdhandler"
    assert handler.description == "cmdhandler command"

    @bot.command(name="cmdname")
    def cmd_handler(message: Message):
        pass

    handler = bot._dispatcher._handlers.get("/cmdname")
    assert handler is not None
    assert handler.name == "Cmdname"
    assert handler.command == "/cmdname"
    assert handler.description == "cmdname command"

    @bot.command(name="cmdname", body="/cmdbody")
    def cmd_handler(message: Message):
        pass

    handler = bot._dispatcher._handlers.get("/cmdbody")
    assert handler is not None
    assert handler.name == "Cmdname"
    assert handler.command == "/cmdbody"
    assert handler.description == "cmdname command"

    @bot.command(use_as_default_handler=True)
    def default_handler(message: Message):
        pass

    handler = bot._dispatcher._default_handler
    assert handler is not None
    assert handler.name == "Defaulthandler"
    assert handler.command == "/defaulthandler"
    assert handler.description == "defaulthandler command"


def test_handlers(test_command_data):
    bot = Bot()
    bot.start()

    test_array = []

    @bot.command
    def cmd_command(message: Message):
        test_array.append(message.body)

    bot.parse_command(test_command_data)
    bot.stop()

    assert test_array[0] == test_command_data["command"]["body"]


def test_command_handler_status():
    bot = Bot()
    bot.start()

    @bot.command
    def cmd_command(message: Message):
        ...

    assert bot._dispatcher._handlers.get("/cmd").to_status_command().dict() == {
        "name": "Cmd",
        "body": "/cmd",
        "description": "cmd command",
        "options": {},
        "elements": [],
    }
