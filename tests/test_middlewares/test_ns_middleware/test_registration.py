import pytest

from botx.middlewares.ns import NextStepMiddleware, register_function_as_ns_handler


def test_register_middleware_with_functions_dict(bot, build_handler_for_collector):
    functions = {"ns_handler": build_handler_for_collector("ns_handler")}

    bot.add_middleware(NextStepMiddleware, bot=bot, functions=functions)

    assert [bot.state.ns_collector.handler_for(name) for name in functions]


def test_register_ns_middleware_using_functions_set(bot, build_handler_for_collector):
    functions = {build_handler_for_collector("ns_handler")}

    bot.add_middleware(NextStepMiddleware, bot=bot, functions=functions)

    assert [bot.state.ns_collector.handler_for(name) for name in ["ns_handler"]]


def test_no_duplicate_handlers_registration(bot, build_handler_for_collector):
    bot.add_middleware(NextStepMiddleware, bot=bot, functions={})

    handler = build_handler_for_collector("ns_handler")

    register_function_as_ns_handler(bot, handler)

    with pytest.raises(ValueError):
        register_function_as_ns_handler(bot, handler)


def test_register_break_handler_as_string(bot, build_handler_for_collector):
    bot.handler(handler=build_handler_for_collector("break_handler"), command="/break")

    bot.add_middleware(
        NextStepMiddleware,
        bot=bot,
        functions={},
        break_handler="break_handler",
    )

    assert bot.state.ns_collector.handler_for("break_handler") == bot.handler_for(
        "break_handler",
    )


def test_register_break_handler_as_handler(bot, build_handler_for_collector):
    bot.handler(build_handler_for_collector("break_handler"), command="/break")

    bot.add_middleware(
        NextStepMiddleware,
        bot=bot,
        functions={},
        break_handler=bot.handler_for("break_handler"),
    )

    assert bot.state.ns_collector.handler_for("break_handler") == bot.handler_for(
        "break_handler",
    )


def test_register_break_handler_as_function(bot, build_handler_for_collector):
    handler = build_handler_for_collector("break_handler")
    bot.add_middleware(
        NextStepMiddleware,
        bot=bot,
        functions={},
        break_handler=handler,
    )

    assert bot.state.ns_collector.handler_for("break_handler").handler == handler
