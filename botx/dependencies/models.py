"""Dependant model and transforming functions."""

import inspect
from typing import Callable, List, Optional, Tuple

from pydantic import BaseModel, validator
from pydantic.utils import lenient_issubclass

from botx import bots
from botx.clients import AsyncClient, Client
from botx.dependencies import inspecting
from botx.models.messages import Message


class Depends:
    """Stores dependency callable."""

    def __init__(self, dependency: Callable, *, use_cache: bool = True) -> None:
        """Store callable for dependency, if None then will be retrieved from signature.

        Arguments:
            dependency: callable object that will be used in handlers or other
                dependencies instances.
            use_cache: use cache for dependency.
        """
        self.dependency = dependency
        self.use_cache = use_cache


DependantCache = Tuple[Optional[Callable], Tuple[str, ...]]


class Dependant(BaseModel):  # noqa: WPS230
    """Main model that contains all necessary data for solving dependencies."""

    dependencies: List["Dependant"] = []
    """list of sub-dependencies for this dependency."""
    name: Optional[str] = None
    """name of dependency."""
    call: Optional[Callable] = None
    """callable object that will solve dependency."""
    message_param_name: Optional[str] = None
    """param name for passing incoming [message][botx.models.messages.Message]."""
    bot_param_name: Optional[str] = None
    """param name for passing [bot][botx.bots.Bot] that handles command."""
    async_client_param_name: Optional[str] = None
    """param name for passing [client][botx.clients.AsyncClient] for sending requests
    manually from async handlers."""
    sync_client_param_name: Optional[str] = None
    use_cache: bool = True
    """use cache for optimize solving performance."""

    # Save the cache key at creation to optimize performance
    cache_key: DependantCache = (None, ())
    """Storage for cache."""

    @validator("cache_key", always=True)
    def init_cache(
        cls, _: DependantCache, values: dict  # noqa: N805
    ) -> DependantCache:
        """Init cache for dependency with passed call and empty tuple.

        Arguments:
            _: init value for cache. Mainly won't be used in initialization.
            values: already validated values.

        Returns:
            Cache for callable.
        """
        return values["call"], tuple((set()))


Dependant.update_forward_refs()


def get_param_sub_dependant(*, param: inspect.Parameter) -> Dependant:
    """Parse instance of parameter to get it as dependency.

    Arguments:
        param: param for which sub dependency should be retrieved.

    Returns:
        Object that will be used in solving dependency.
    """
    depends: Depends = param.default
    dependency = depends.dependency

    return get_dependant(call=dependency, name=param.name, use_cache=depends.use_cache)


def get_dependant(
    *, call: Callable, name: Optional[str] = None, use_cache: bool = True
) -> Dependant:
    """Get dependant instance from passed callable object.

    Arguments:
        call: callable object that will be parsed to get required parameters and
            sub dependencies.
        name: name for dependency.
        use_cache: use cache for optimize solving performance.

    Returns:
        Object that will be used in solving dependency.
    """
    dependant = Dependant(call=call, name=name, use_cache=use_cache)
    for param in inspecting.get_typed_signature(call).parameters.values():
        if isinstance(param.default, Depends):
            dependant.dependencies.append(get_param_sub_dependant(param=param))
            continue
        if add_special_param_to_dependency(param=param, dependant=dependant):
            continue

        raise ValueError(
            f"Param {param.name} can only be a dependency, message, bot or client"
        )

    return dependant


def add_special_param_to_dependency(
    *, param: inspect.Parameter, dependant: Dependant
) -> bool:
    """Check if param is non field object that should be passed into callable.

    Arguments:
        param: param that should be checked.
        dependant: dependency which field would be filled with required param name.

    Returns:
        Result of check.
    """
    if lenient_issubclass(param.annotation, bots.Bot):
        dependant.bot_param_name = param.name
        return True
    elif lenient_issubclass(param.annotation, Message):
        dependant.message_param_name = param.name
        return True
    elif lenient_issubclass(param.annotation, AsyncClient):
        dependant.async_client_param_name = param.name
        return True
    elif lenient_issubclass(param.annotation, Client):
        dependant.sync_client_param_name = param.name
        return True

    return False
