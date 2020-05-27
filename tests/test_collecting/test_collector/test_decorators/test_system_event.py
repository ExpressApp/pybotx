from botx import SystemEvents

pytest_plugins = ("tests.test_collecting.fixtures",)


def test_registration_handler_for_several_system_events(
    handler_as_function, extract_collector, collector_cls
):
    system_events = {SystemEvents.chat_created, SystemEvents.file_transfer}
    collector = collector_cls()
    collector.system_event(
        handler=handler_as_function, events=list(system_events),
    )
    assert [SystemEvents(handler.body) for handler in collector.handlers]
