from botx import Status, StatusResult


def test_base_dispatcher_attributes(custom_dispatcher):
    assert custom_dispatcher._handlers == {}
    assert custom_dispatcher._default_handler is None


def test_base_dispatcher_separate_handlers(custom_dispatcher, custom_handler):
    custom_dispatcher2 = custom_dispatcher.__class__()
    custom_dispatcher.add_handler(custom_handler)
    assert custom_dispatcher._handlers != custom_dispatcher2._handlers


def test_base_dispatcher_status_creation(
    custom_dispatcher, custom_handler, custom_default_handler
):
    assert custom_dispatcher._create_status() == Status(result=StatusResult())

    custom_dispatcher._default_handler = custom_default_handler
    assert custom_dispatcher._create_status() == Status(result=StatusResult())

    custom_dispatcher._handlers = {custom_handler.command: custom_handler}
    assert custom_dispatcher._create_status() == Status(
        result=StatusResult(commands=[custom_handler.to_status_command()])
    )


def test_base_dispatcher_add_handler(
    custom_dispatcher, custom_handler, custom_default_handler
):
    assert custom_dispatcher._create_status() == Status(result=StatusResult())

    custom_dispatcher.add_handler(custom_default_handler)
    assert custom_dispatcher._create_status() == Status(result=StatusResult())

    custom_dispatcher.add_handler(custom_handler)
    assert custom_dispatcher._create_status() == Status(
        result=StatusResult(commands=[custom_handler.to_status_command()])
    )
