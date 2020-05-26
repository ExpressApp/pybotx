"""Some helper functions that are used in library."""

import inspect
from typing import Callable, List, Optional, Sequence, TypeVar

TSequenceElement = TypeVar("TSequenceElement")


def optional_sequence_to_list(
    seq: Optional[Sequence[TSequenceElement]] = None,
) -> List[TSequenceElement]:
    """Convert optional sequence of elements to list.

    Arguments:
        seq: sequence that should be converted to list.

    Returns:
        List of passed elements.
    """
    return list(seq or [])


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
