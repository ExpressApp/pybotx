import pytest

from botx import CommandCallback, CommandHandler, MenuCommand


def test_command_handler_status_representation(handler_factory):
    handler_name = "handler"

    handler = CommandHandler(
        command=f"/{handler_name}",
        menu_command=f"/{handler_name}",
        regex_command=f"/{handler_name}",
        name=handler_name,
        description=f"{handler_name.capitalize()} handler",
        callback=CommandCallback(callback=handler_factory("sync")),
    )

    assert handler.to_status_command() == MenuCommand(
        name=handler_name,
        body=f"/{handler_name}",
        description=f"{handler_name.capitalize()} handler",
        options=[],
        elements=[],
    )

    handler.exclude_from_status = True
    assert not handler.to_status_command()

    handler.exclude_from_status = False
    handler.use_as_default_handler = True
    assert not handler.to_status_command()


def test_command_handler_callback_does_not_accept_not_primitives():
    class CustomClass:
        pass

    with pytest.raises(ValueError):
        CommandCallback(callback=lambda: None, command_params={"key": CustomClass})
