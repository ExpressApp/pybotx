from botx import CommandHandler, MenuCommand


def test_command_handler_to_status_with_simple_handler():
    ch = CommandHandler(
        name="handler", command="/cmd", description="command handler", func=lambda x: x
    )
    assert ch.to_status_command() == MenuCommand(
        body="/cmd",
        name="handler",
        description="command handler",
        options=[],
        elements=[],
    )


def test_command_handler_to_status_with_default_handler():
    ch = CommandHandler(
        name="handler",
        command="/cmd",
        description="command handler",
        func=lambda x: x,
        use_as_default_handler=True,
    )
    assert not ch.to_status_command()


def test_command_handler_to_status_with_system_command_handler():
    ch = CommandHandler(
        name="handler",
        command="/cmd",
        description="command handler",
        func=lambda x: x,
        use_as_default_handler=True,
    )
    assert not ch.to_status_command()


def test_command_handler_to_status_with_exclude_from_status():
    ch = CommandHandler(
        name="handler",
        command="/cmd",
        description="command handler",
        func=lambda x: x,
        use_as_default_handler=True,
    )
    assert not ch.to_status_command()
