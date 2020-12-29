from typing import Callable

import pytest

from botx import Collector, Depends

pytest_plugins = ("tests.test_collecting.fixtures",)


def build_botx_dependency(number: int) -> Callable[[], None]:
    def factory():
        """Just do nothing."""

    factory.number = number
    return factory


@pytest.fixture()
def build_dependency():
    return build_botx_dependency


def test_preserving_order_after_merging(message, handler_as_function, build_dependency):
    message.command.body = "/command"

    collector1 = Collector(dependencies=[Depends(build_dependency(1))])
    collector2 = Collector(dependencies=[Depends(build_dependency(2))])

    collector2.add_handler(
        handler=handler_as_function,
        body=message.command.command,
        dependencies=[Depends(build_dependency(3))],
    )

    collector1.include_collector(collector2)

    handler = collector1.handler_for("handler_function")

    numbers = [dep.dependency.number for dep in handler.dependencies]

    assert numbers == [1, 2, 3]


def test_preserving_order_after_merging_for_default_handler(
    message, default_handler, build_dependency,
):
    message.command.body = "/command"

    default_handler.dependencies = [Depends(build_dependency(3))]

    collector1 = Collector(dependencies=[Depends(build_dependency(1))])
    collector2 = Collector(
        dependencies=[Depends(build_dependency(2))], default=default_handler,
    )

    collector1.include_collector(collector2)

    handler = collector1.default_message_handler

    numbers = [dep.dependency.number for dep in handler.dependencies]

    assert numbers == [1, 2, 3]


def test_dependencies_order_in_include_collector(
    message, handler_as_function, build_dependency,
):
    message.command.body = "/command"

    collector1 = Collector()
    collector2 = Collector()

    collector2.add_handler(
        handler=handler_as_function,
        body=message.command.command,
        dependencies=[Depends(build_dependency(2))],
    )

    collector1.include_collector(
        collector2, dependencies=[Depends(build_dependency(1))],
    )

    handler = collector1.handler_for("handler_function")

    numbers = [dep.dependency.number for dep in handler.dependencies]

    assert numbers == [1, 2]
