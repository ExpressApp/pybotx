import pytest

from botx import Bot
from botx.collecting import Collector, Handler


class HandlerClass:
    def handler_method_snake_case(self) -> None:
        """Handler with name in snake case."""

    def handlerMethodCamelCase(self) -> None:
        """Handler with name in camel case."""

    def HandlerMethodPascalCase(self) -> None:
        """Handler with name in pascal case."""

    def __call__(self) -> None:
        """Handler that is callable class."""


@pytest.fixture()
def handler_as_function(build_handler_for_collector):
    return build_handler_for_collector("handler_function")


@pytest.fixture()
def handler_as_class():
    return HandlerClass


@pytest.fixture()
def handler_as_callable_object():
    return HandlerClass()


@pytest.fixture()
def handler_as_normal_method():
    return HandlerClass().handler_method_snake_case


@pytest.fixture()
def handler_as_pascal_case_method():
    return HandlerClass().HandlerMethodPascalCase


@pytest.fixture()
def handler_as_camel_case_method():
    return HandlerClass().handlerMethodCamelCase


@pytest.fixture()
def default_handler(handler_as_function):
    return Handler(handler=handler_as_function, body="/default-handler")


@pytest.fixture()
def extract_collector():
    def factory(collector_instance):
        if isinstance(collector_instance, Bot):
            return collector_instance.collector

        return collector_instance

    return factory


@pytest.fixture(params=(Collector, Bot))
def collector_cls(request):
    return request.param
