from botx import CommandHandler, CommandRouter


def test_router_commands_adding(
    custom_router, custom_async_handler, custom_default_handler
):
    custom_router.add_handler(custom_async_handler)
    custom_router.add_handler(custom_default_handler)

    assert len(custom_router._handlers) == 2


def test_router_commands_nesting(
    custom_default_handler,
    custom_async_handler,
    custom_handler,
    custom_default_async_handler,
):
    router1 = CommandRouter()

    router1.add_handler(custom_default_handler)
    router1.add_handler(custom_async_handler)

    router2 = CommandRouter()
    router2.add_handler(custom_handler)
    router2.add_handler(custom_default_async_handler)

    assert len(router2._handlers) == 2

    router2.add_commands(router1)

    assert len(router2._handlers) == 3
    assert router2._handlers[custom_default_handler.command].use_as_default_handler


def test_router_command_decorator_simple(custom_router):
    @custom_router.command
    def func(m, b):
        pass

    assert len(custom_router._handlers) == 1
    assert "/func" in custom_router._handlers
    assert custom_router._handlers["/func"] == CommandHandler(
        command="/func", func=func.func, name="func", description="func command"
    )


def test_router_command_decorator_call_simple(custom_router):
    @custom_router.command()
    def func(m, b):
        pass

    assert len(custom_router._handlers) == 1
    assert "/func" in custom_router._handlers
    assert custom_router._handlers["/func"] == CommandHandler(
        command="/func", func=func.func, name="func", description="func command"
    )


def test_router_command_decorator_with_name(custom_router):
    @custom_router.command(name="handler")
    def func(m):
        pass

    assert len(custom_router._handlers) == 1
    assert "/handler" in custom_router._handlers
    assert custom_router._handlers["/handler"] == CommandHandler(
        command="/handler",
        func=func.func,
        name="handler",
        description="handler command",
    )


def test_router_command_decorator_with_docstring(custom_router):
    @custom_router.command(name="handler")
    def func(m):
        """func command"""

    assert len(custom_router._handlers) == 1
    assert "/handler" in custom_router._handlers
    assert custom_router._handlers["/handler"] == CommandHandler(
        command="/handler", func=func.func, name="handler", description="func command"
    )


def test_router_command_decorator_with_full_args(custom_router):
    @custom_router.command(
        name="handler", body="/function", description="command description"
    )
    def func(m, b):
        """func command"""

    assert custom_router._handlers["/function"] == CommandHandler(
        command="/function",
        func=func.func,
        name="handler",
        description="command description",
    )
