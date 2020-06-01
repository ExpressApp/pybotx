"""Wrappers around param classes that are used in handlers or dependencies."""

from typing import Any, Callable

from botx.dependencies import models


def Depends(dependency: Callable, *, use_cache: bool = True) -> Any:  # noqa: N802
    """Wrap Depends param for using in handlers.

    Arguments:
        dependency: callable object that will be used in handlers or other dependencies
            instances.
        use_cache: use cache for dependency.

    Returns:
        [Depends][botx.dependencies.models.Depends] that wraps passed callable.
    """
    return models.Depends(dependency=dependency, use_cache=use_cache)
