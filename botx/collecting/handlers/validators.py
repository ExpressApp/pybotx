"""Validator for Handler."""
import inspect
from typing import Callable, List, Optional

from botx.collecting.handlers.name_generators import get_name_from_callable
from botx.collecting.handlers.value_extractor import get_value
from botx.dependencies.models import Dependant, Depends, get_dependant
from botx.dependencies.solving import get_executor


def validate_body_for_status(executor: Callable, values: dict) -> Callable:
    """Validate that body is acceptable for status.

    Arguments:
        executor: executor that will be just returned from validator.
        values: already checked values.

    Returns:
        Passed executor.

    Raises:
        ValueError: raised if body is not acceptable for status.
    """
    include_in_status = get_value("include_in_status", values)
    if not include_in_status:
        return executor

    body = get_value("body", values)

    if not body.startswith("/"):
        raise ValueError("public commands should start with leading slash")

    slash_part_of_body = body[: -len(body.strip("/"))]
    if slash_part_of_body.count("/") != 1:
        raise ValueError("command body can contain only single leading slash")

    if len(body.split()) != 1:
        raise ValueError("public commands should contain only one word")

    return executor


def retrieve_name_for_handler(name: Optional[str], values: dict) -> str:
    """Retrieve name for handler.

    Arguments:
        name: passed name for handler.
        values: already checked values.

    Returns:
        Name for handler.
    """
    return name or get_name_from_callable(get_value("handler", values))


def retrieve_full_description_for_handler(full_description: str, values: dict) -> str:
    """Retrieve full description for handler.

    Arguments:
        full_description: passed name for handler.
        values: already checked values.

    Returns:
        Full description for handler.
    """
    return full_description or inspect.cleandoc(
        get_value("handler", values).__doc__ or "",
    )


def check_handler_is_function(handler: Callable) -> Callable:
    """Check handler can be proceed by library.

    Library can handle functions and methods as handlers.

    Arguments:
        handler: passed handler callable.

    Returns:
        Passed handler.

    Raises:
        ValueError: raised if handler is not acceptable.
    """
    if not (inspect.isfunction(handler) or inspect.ismethod(handler)):
        raise ValueError("handler must be a function or method")

    return handler


def retrieve_dependant(_dependant: None, values: dict) -> Dependant:
    """Retrieve dependant for handler.

    Arguments:
        _dependant: default dependant that is always `None`.
        values: already validated values.

    Returns:
        Generated dependant object.
    """
    return get_dependant(call=get_value("handler", values))


def retrieve_dependencies(dependencies: List[Depends], values: dict) -> List[Depends]:
    """Retrieve dependencies for handler.

    Arguments:
        dependencies: passed dependencies.
        values: already validated values.

    Returns:
        Passed dependencies.

    Raises:
        ValueError: raised if dependency `call` attribute is not callable.
    """
    dependant = get_value("dependant", values)
    for index, depends in enumerate(dependencies):
        if not callable(depends.dependency):
            raise ValueError("a parameter-less dependency must have a callable")

        dependant.dependencies.insert(
            index, get_dependant(call=depends.dependency, use_cache=depends.use_cache),
        )
    return dependencies


def retrieve_executor(_executor: None, values: dict) -> Callable:
    """Retrieve executor for handler.

    Arguments:
        _executor: default executor that is always `None`.
        values: already validated values.

    Returns:
        Passed executor.
    """
    return get_executor(
        dependant=get_value("dependant", values),
        dependency_overrides_provider=get_value(
            "dependency_overrides_provider", values,
        ),
    )
