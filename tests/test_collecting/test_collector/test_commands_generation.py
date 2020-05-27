import pytest

from botx.exceptions import NoMatchFound

pytest_plugins = ("tests.test_collecting.fixtures",)


def test_error_when_no_args_passed(collector_cls):
    collector = collector_cls()
    with pytest.raises(TypeError):
        collector.command_for()


def test_building_command_with_arguments(handler_as_function, collector_cls):
    collector = collector_cls()
    collector.add_handler(handler=handler_as_function, name="handler", body="/handler")
    built_command = collector.command_for("handler", "arg1", 1, True)
    assert built_command == "/handler arg1 1 True"


def test_raising_exception_when_generating_command_and_not_found(
    build_handler_for_collector, collector_cls
):
    collector = collector_cls()
    collector.handler(build_handler_for_collector("handler1"))
    collector.handler(build_handler_for_collector("handler2"))
    with pytest.raises(NoMatchFound):
        collector.command_for("not-existing-handler")
