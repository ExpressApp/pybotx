"""Dependant model and transforming functions."""

import inspect
from typing import Callable, List, Optional, Tuple

from pydantic import BaseModel, validator
from pydantic.utils import lenient_issubclass

from botx.bots import bots
from botx.clients.clients.async_client import AsyncClient
from botx.clients.clients.sync_client import Client
from botx.dependencies import inspecting
from botx.models.messages import Message

WRONG_PARAM_TYPE_ERROR_TEXT = (
    "Param {0} of {1} can only be a dependency, message, bot or client, got: {2}"
)


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


class Dependant(BaseModel):
    """Main model that contains all necessary data for solving dependencies."""

    #: list of sub-dependencies for this dependency.
    dependencies: List["Dependant"] = []

    #: name of dependency.
    name: Optional[str] = None

    #: callable object that will solve dependency.
    call: Optional[Callable] = None

    #: param name for passing incoming [message][botx.models.messages.Message]
    message_param_name: Optional[str] = None

    #: param name for passing [bot][botx.bots.Bot] that handles command.
    bot_param_name: Optional[str] = None

    #: param name for passing [client][botx.clients.clients.async_client.AsyncClient].
    async_client_param_name: Optional[str] = None

    #: param name for passing [client][botx.clients.clients.sync_client.Client].
    sync_client_param_name: Optional[str] = None

    #: use cache for optimize solving performance.
    use_cache: bool = True

    # Save the cache key at creation to optimize performance
    #: storage for cache.
    cache_key: DependantCache = (None, ())

    @validator("cache_key", always=True)
    def init_cache(
        cls, _: DependantCache, values: dict,
    ) -> DependantCache:
        """Init cache for dependency with passed call and empty tuple.

        Arguments:
            cls: this class.
            _: init value for cache. Mainly won't be used in initialization.
            values: already validated values.

        Returns:
            Cache for callable.
        """
        return values["call"], tuple((set()))


Dependant.update_forward_refs()


def get_param_sub_dependant(*, dependency_param: inspect.Parameter) -> Dependant:
    """Parse instance of parameter to get it as dependency.

    Arguments:
        dependency_param: param for which sub dependency should be retrieved.

    Returns:
        Object that will be used in solving dependency.
    """
    depends: Depends = dependency_param.default
    dependency = depends.dependency

    return get_dependant(
        call=dependency, name=dependency_param.name, use_cache=depends.use_cache,
    )


def get_dependant(
    *, call: Callable, name: Optional[str] = None, use_cache: bool = True,
) -> Dependant:
    """Get dependant instance from passed callable object.

    Arguments:
        call: callable object that will be parsed to get required parameters and
            sub dependencies.
        name: name for dependency.
        use_cache: use cache for optimize solving performance.

    Returns:
        Object that will be used in solving dependency.

    Raises:
        ValueError: raised if param is not Dependant or special type.
    """
    dependant = Dependant(call=call, name=name, use_cache=use_cache)
    for dependency_param in inspecting.get_typed_signature(call).parameters.values():
        if isinstance(dependency_param.default, Depends):
            dependant.dependencies.append(
                get_param_sub_dependant(dependency_param=dependency_param),
            )
            continue

        is_special_param = add_special_param_to_dependency(
            dependency_param=dependency_param, dependant=dependant,
        )
        if is_special_param:
            continue

        raise ValueError(
            WRONG_PARAM_TYPE_ERROR_TEXT.format(
                dependency_param.name, call, dependency_param.annotation,
            ),
        )

    return dependant


def add_special_param_to_dependency(
    *, dependency_param: inspect.Parameter, dependant: Dependant,
) -> bool:
    """Check if param is non field object that should be passed into callable.

    Arguments:
        dependency_param: param that should be checked.
        dependant: dependency which field would be filled with required param name.

    Returns:
        Result of check.
    """
    if lenient_issubclass(dependency_param.annotation, bots.Bot):
        dependant.bot_param_name = dependency_param.name
        return True
    elif lenient_issubclass(dependency_param.annotation, Message):
        dependant.message_param_name = dependency_param.name
        return True
    elif lenient_issubclass(dependency_param.annotation, AsyncClient):
        dependant.async_client_param_name = dependency_param.name
        return True
    elif lenient_issubclass(dependency_param.annotation, Client):
        dependant.sync_client_param_name = dependency_param.name
        return True

    return False
