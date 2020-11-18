from botx import Collector
from botx.models.command import CommandDescriptor

pytest_plugins = ("tests.test_collecting.fixtures",)


def test_defining_handler_in_collector_as_decorator(
    handler_as_function, extract_collector, collector_cls,
):
    collector = Collector()
    collector.handler()(handler_as_function)
    handlers = [collector.handler_for("handler_function")]
    assert handlers


def test_handler_command_descriptor(
    handler_as_function, extract_collector, collector_cls,
):
    collector = collector_cls()
    command_descriptor = CommandDescriptor(
        command="/test", name="name:test", description="short", full_description="full"
    )
    collector.handler(command_descriptor=command_descriptor)(handler_as_function)
    handler = collector.handlers[0]
    assert handler.body == "/test"
    assert handler.name == "name:test"
    assert handler.full_description == "full"
    assert handler.description == "short"


def test_handler_two_commands_descriptor(
    handler_as_function, extract_collector, collector_cls,
):
    collector = collector_cls()
    command_descriptor = CommandDescriptor(
        commands=["/cmd1", "/cmd2"],
        name="name:test",
        description="short",
        full_description="full",
    )
    collector.handler(command_descriptor=command_descriptor)(handler_as_function)
    assert collector.handlers[0].body == "/cmd1"
    assert collector.handlers[0].name == "name:test"
    assert collector.handlers[0].full_description == "full"
    assert collector.handlers[0].description == "short"

    assert collector.handlers[1].body == "/cmd2"
    assert collector.handlers[1].name == "name:test"
    assert collector.handlers[1].full_description == "full"
    assert collector.handlers[1].description == "short"
