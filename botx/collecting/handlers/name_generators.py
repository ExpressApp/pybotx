"""Generators for names for handler."""

import inspect
import re
from typing import Callable


def get_body_from_name(name: str) -> str:
    """Get auto body from given handler name in format `/word-word`.

    Examples:
        ```
        >>> get_body_from_name("HandlerFunction")
        "handler-function"
        >>> get_body_from_name("handlerFunction")
        "handler-function"
        ```
    Arguments:
        name: name of handler for which body should be generated.
    """
    splited_words = re.findall(r"^[a-z\d_\-]+|[A-Z\d_\-][^A-Z\d_\-]*", name)
    joined_body = "-".join(splited_words)
    dashed_body = joined_body.replace("_", "-")
    return "/{0}".format(re.sub("-+", "-", dashed_body).lower())


def get_name_from_callable(handler: Callable) -> str:
    """Get auto name from given callable object.

    Arguments:
        handler: callable object that will be used to retrieve auto name for handler.

    Returns:
        Name obtained from callable.
    """
    is_function = inspect.isfunction(handler)
    is_method = inspect.ismethod(handler)
    is_class = inspect.isclass(handler)
    if is_function or is_method or is_class:
        return handler.__name__
    return handler.__class__.__name__
