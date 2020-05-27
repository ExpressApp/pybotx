from botx import Collector

pytest_plugins = ("tests.test_collecting.fixtures",)


def test_generating_body_from_snake_case(handler_as_normal_method,):
    collector = Collector()
    collector.add_handler(handler=handler_as_normal_method)
    handler = collector.handler_for("handler_method_snake_case")
    assert handler.body == "/handler-method-snake-case"


def test_generating_body_from_pascal_case(handler_as_pascal_case_method):
    collector = Collector()
    collector.add_handler(handler=handler_as_pascal_case_method)
    handler = collector.handler_for("HandlerMethodPascalCase")
    assert handler.body == "/handler-method-pascal-case"


def test_generating_body_from_camel_case(handler_as_camel_case_method):
    collector = Collector()
    collector.add_handler(handler=handler_as_camel_case_method)
    handler = collector.handler_for("handlerMethodCamelCase")
    assert handler.body == "/handler-method-camel-case"
