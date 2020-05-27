from botx.collecting import Handler

pytest_plugins = ("tests.test_collecting.fixtures",)


def test_no_extra_space_on_command_built_through_command_for(handler_as_function):
    handler = Handler(body="/command", handler=handler_as_function,)

    assert handler.command_for() == "/command"

    built_command_with_args = handler.command_for(None, 1, "some string", True)

    assert built_command_with_args == "/command 1 some string True"
