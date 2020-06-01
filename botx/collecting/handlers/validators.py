"""Validators and extractors for Handler fields."""
import inspect
from typing import Any, Callable, List, Optional

from botx.collecting.handlers.name_generators import get_name_from_callable
from botx.dependencies.models import Dependant, Depends, get_dependant
from botx.dependencies.solving import get_executor


def validate_body_for_status(executor: Callable, values: dict) -> Callable:
    """Validate that body is acceptable for status.

    Arguments:
        executor: executor that will be just returned from validator.
        values: already checked validated_values.

    Returns:
        Passed executor.

    Raises:
        ValueError: raised if body is not acceptable for status.
    """
    include_in_status = values["include_in_status"]
    if not include_in_status:
        return executor

    body = values["body"]

    if not body.startswith("/"):
        raise ValueError("public commands should start with leading slash")

    slash_part_of_body = body[: -len(body.strip("/"))]
    if slash_part_of_body.count("/") != 1:
        raise ValueError("command body can contain only single leading slash")

    if len(body.split()) != 1:
        raise ValueError("public commands should contain only one word")

    return executor


def retrieve_name_for_handler(name: Optional[str], handler: Callable) -> str:
    """Retrieve name for handler.

    Arguments:
        name: passed name for handler.
        handler: handler that will be used to generate name.

    Returns:
        Name for handler.
    """
    return name or get_name_from_callable(handler)


def retrieve_full_description_for_handler(
    full_description: Optional[str], handler: Callable,
) -> str:
    """Retrieve full description for handler.

    Arguments:
        full_description: passed name for handler.
        handler: handler from which docstring will be used.

    Returns:
        Full description for handler.
    """
    return full_description or inspect.cleandoc(handler.__doc__ or "")


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


def retrieve_dependant(handler: Callable, dependencies: List[Depends]) -> Dependant:
    """Retrieve dependant for handler.

    Arguments:
        handler: handler for which dependant should be created.
        dependencies: passed background dependencies.

    Returns:
        Generated dependant object.
    """
    dependant = get_dependant(call=handler)
    for index, depends in enumerate(dependencies):
        dependant.dependencies.insert(
            index, get_dependant(call=depends.dependency, use_cache=depends.use_cache),
        )

    return dependant


def retrieve_executor(
    dependant: Dependant, dependency_overrides_provider: Any,
) -> Callable:
    """Retrieve executor for handler.

    Arguments:
        dependant: dependant that will be used to generate executor.
        dependency_overrides_provider: overrider for dependencies.

    Returns:
        Generated executor.
    """
    return get_executor(
        dependant=dependant,
        dependency_overrides_provider=dependency_overrides_provider,
    )
