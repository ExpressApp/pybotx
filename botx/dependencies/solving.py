"""Functions for solving dependencies."""

from collections import Callable
from typing import Any, Dict, Optional, Tuple, cast

from botx import concurrency
from botx.dependencies.models import Dependant, get_dependant
from botx.models.messages import Message

CacheKey = Tuple[Callable, Tuple[str, ...]]
DependenciesCache = Dict[CacheKey, Any]


async def solve_sub_dependency(
    message: Message,
    dependant: Dependant,
    values: Dict[str, Any],
    dependency_overrides_provider: Any,
    dependency_cache: Dict[CacheKey, Any],
) -> None:
    """Solve single sub dependency.

    Arguments:
        message: incoming message that is used for solving this sub dependency.
        dependant: dependency that is solving while calling this function.
        values: already filled values that are required for this dependency.
        dependency_overrides_provider: an object with `dependency_overrides` attribute
            that contains overrides for dependencies.
        dependency_cache: cache that contains already solved dependency and result for
            it.
    """
    call = cast(Callable, dependant.call)
    use_sub_dependant = dependant

    overrides = getattr(dependency_overrides_provider, "dependency_overrides", {})
    if overrides:
        call = overrides.get(dependant.call, dependant.call)
        use_sub_dependant = get_dependant(call=call, name=dependant.name)

    sub_values, sub_dependency_cache = await solve_dependencies(
        message=message,
        dependant=use_sub_dependant,
        dependency_overrides_provider=dependency_overrides_provider,
        dependency_cache=dependency_cache,
    )
    dependency_cache.update(sub_dependency_cache)

    dependant.cache_key = cast(CacheKey, dependant.cache_key)
    if dependant.use_cache and dependant.cache_key in dependency_cache:
        solved = dependency_cache[dependant.cache_key]
    else:
        solved = await concurrency.callable_to_coroutine(call, **sub_values)

    if dependant.name is not None:
        values[dependant.name] = solved
    if dependant.cache_key not in dependency_cache:
        dependency_cache[dependant.cache_key] = solved


async def solve_dependencies(
    *,
    message: Message,
    dependant: Dependant,
    dependency_overrides_provider: Any = None,
    dependency_cache: Optional[Dict[CacheKey, Any]] = None,
) -> Tuple[Dict[str, Any], DependenciesCache]:
    """Resolve all required dependencies for Dependant using incoming message.

    Arguments:
        message: incoming Message with all necessary data.
        dependant: Dependant object for which all sub dependencies should be solved.
        dependency_overrides_provider: an object with `dependency_overrides` attribute
            that contains overrides for dependencies.
        dependency_cache: cache that contains already solved dependency and result for
            it.

    Returns:
        Keyword arguments with their vales and cache.
    """
    values: Dict[str, Any] = {}
    dependency_cache = dependency_cache or {}
    for sub_dependant in dependant.dependencies:
        await solve_sub_dependency(
            message=message,
            dependant=sub_dependant,
            values=values,
            dependency_overrides_provider=dependency_overrides_provider,
            dependency_cache=dependency_cache,
        )

    if dependant.message_param_name:
        values[dependant.message_param_name] = message
    if dependant.bot_param_name:
        values[dependant.bot_param_name] = message.bot
    if dependant.async_client_param_name:
        values[dependant.async_client_param_name] = message.bot.client
    if dependant.sync_client_param_name:
        values[dependant.sync_client_param_name] = message.bot.sync_client
    return values, dependency_cache
