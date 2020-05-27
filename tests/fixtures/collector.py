from typing import Callable, Optional

import pytest

from botx import Collector, Depends, Message


def build_botx_handler(name: Optional[str] = None) -> Callable[[], None]:
    def factory(_message: Message):
        """Just do nothing."""

    factory.__name__ = name or factory.__name__
    return factory


@pytest.fixture()
def build_handler_for_collector():
    return build_botx_handler


@pytest.fixture()
def collector_with_handlers(build_handler_for_collector):
    collector = Collector()
    collector.handler(build_handler_for_collector("regular_handler"))
    collector.handler(
        build_handler_for_collector("regular_handler_with_command"),
        command="/handler-command",
    )
    collector.handler(
        build_handler_for_collector("regular_handler_with_command_aliases"),
        commands=["/handler-command1", "/handler-command2"],
    )
    collector.handler(
        build_handler_for_collector("regular_handler_with_command_and_command_aliases"),
        command="/handler-command3",
        commands=["/handler-command4", "/handler-command5"],
    )
    collector.handler(
        build_handler_for_collector("regular_handler_with_custom_name"),
        name="regular-handler-with-name",
    )
    collector.handler(
        build_handler_for_collector("regular_handler_with_background_dependencies"),
        dependencies=[Depends(build_handler_for_collector("background_dependency"))],
    )
    collector.handler(
        build_handler_for_collector(
            "regular_handler_that_excluded_from_status_and_auto_body"
        ),
        include_in_status=False,
    )
    collector.handler(
        build_handler_for_collector(
            "regular_handler_that_excluded_from_status_and_passed_body"
        ),
        command="regular-handler-with-excluding-from-status",
        include_in_status=False,
    )
    collector.handler(
        build_handler_for_collector(
            "regular_handler_that_included_in_status_by_callable_function"
        ),
        include_in_status=lambda *_: True,
    )
    collector.handler(
        build_handler_for_collector(
            "regular_handler_that_excluded_from_status_by_callable_function"
        ),
        include_in_status=lambda *_: False,
    )
    collector.default(build_handler_for_collector("default_handler"))
    collector.hidden(build_handler_for_collector("hidden_handler"))
    collector.chat_created(build_handler_for_collector("chat_created_handler"))
    collector.file_transfer(build_handler_for_collector("file_transfer_handler"))
    return collector
