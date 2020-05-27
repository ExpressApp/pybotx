import threading

import pytest

from botx.middlewares.ns import NextStepMiddleware

pytestmark = pytest.mark.asyncio
pytest_plugins = ("tests.test_middlewares.test_ns_middleware.fixtures",)


async def test_executing_ns_handlers(
    bot, incoming_message, client, build_handler_to_start_chain
) -> None:
    chain_start_event = threading.Event()
    ns_handler_event = threading.Event()

    bot.default(handler=build_handler_to_start_chain("ns_handler", chain_start_event))
    bot.add_middleware(
        NextStepMiddleware,
        bot=bot,
        functions={"ns_handler": build_handler_to_start_chain(None, ns_handler_event)},
    )

    incoming_message.command.body = "/start-ns"

    await client.send_command(incoming_message)
    await client.send_command(incoming_message)

    assert chain_start_event.is_set()
    assert ns_handler_event.is_set()


async def test_breaking_chain(
    bot, incoming_message, client, build_handler_to_start_chain
):
    break_handler_event = threading.Event()
    chain_start_event = threading.Event()
    ns_handler_event = threading.Event()

    chain_start_handler = build_handler_to_start_chain("ns_handler", chain_start_event)

    bot.handler(
        handler=build_handler_to_start_chain(None, break_handler_event),
        command="/break",
        name="break_handler",
    )
    bot.handler(handler=chain_start_handler, command="/ns-start", name="chain_start")

    bot.add_middleware(
        NextStepMiddleware,
        bot=bot,
        functions={
            "ns_handler": build_handler_to_start_chain("chain_start", ns_handler_event),
            "chain_start": chain_start_handler,
        },
        break_handler="break_handler",
    )

    incoming_message.command.body = "/ns-start"
    await client.send_command(incoming_message)
    assert chain_start_event.is_set()
    chain_start_event.clear()

    await client.send_command(incoming_message)
    assert ns_handler_event.is_set()
    ns_handler_event.clear()

    await client.send_command(incoming_message)
    assert chain_start_event.is_set()
    chain_start_event.clear()

    incoming_message.command.body = "/break-handler"
    await client.send_command(incoming_message)
    assert break_handler_event.is_set()
