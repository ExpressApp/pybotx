import pytest

from botx import SystemEvents

pytest_plugins = ("tests.test_collecting.fixtures",)


def test_registration_handler_for_several_system_events(
    handler_as_function, extract_collector, collector_cls,
):
    system_events = {
        SystemEvents.chat_created,
        SystemEvents.file_transfer,
        SystemEvents.added_to_chat,
        SystemEvents.deleted_from_chat,
        SystemEvents.left_from_chat,
    }
    collector = collector_cls()
    collector.system_event(
        handler=handler_as_function, events=list(system_events),
    )
    handlers = [SystemEvents(handler.body) for handler in collector.handlers]
    assert handlers


@pytest.mark.parametrize(
    "event",
    [
        SystemEvents.added_to_chat,
        SystemEvents.deleted_from_chat,
        SystemEvents.chat_created,
        SystemEvents.file_transfer,
        SystemEvents.left_from_chat,
    ],
)
def test_defining_system_handler_in_collector_as_decorator(
    handler_as_function, extract_collector, collector_cls, event,
):
    collector = collector_cls()
    getattr(collector, event.name)()(handler_as_function)
    assert SystemEvents(collector.handlers[0].body) == event


def test_error_when_no_event_was_passed(
    handler_as_function, extract_collector, collector_cls,
):
    collector = collector_cls()
    with pytest.raises(AssertionError):
        collector.system_event(handler=handler_as_function)
