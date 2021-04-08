"""Functions for solving dependencies."""

from typing import Any, Awaitable, Callable, Dict, Optional, Tuple, cast

from botx import concurrency
from botx.dependencies.models import (
    CacheKey,
    Dependant,
    DependenciesCache,
    get_dependant,
)
from botx.models.messages.message import Message


async def solve_sub_dependency(
    message: Message,
    dependant: Dependant,
    solved_values: Dict[str, Any],
    dependency_overrides_provider: Any,
    dependency_cache: Dict[CacheKey, Any],
) -> None:
    """
    Solve single sub dependency.

    Arguments:
        message: incoming message that is used for solving this sub dependency.
        dependant: dependency that is solving while calling this function.
        solved_values: already filled validated_values that are required for this
            dependency.
        dependency_overrides_provider: an object with `dependency_overrides` attribute
            that contains overrides for dependencies.
        dependency_cache: cache that contains already solved dependency and result for
            it.

    """
    call = cast(Callable, dependant.call)
    use_sub_dependant = dependant

    overrides = getattr(
        dependency_overrides_provider
        if dependency_overrides_provider is not None
        else message.bot,
        "dependency_overrides",
        {},
    )
    if overrides:
        call = overrides.get(dependant.call, dependant.call)
        use_sub_dependant = get_dependant(call=call, name=dependant.name)

    solving_result = await solve_dependencies(
        message=message,
        dependant=use_sub_dependant,
        dependency_overrides_provider=dependency_overrides_provider,
        dependency_cache=dependency_cache,
    )
    dependency_cache.update(solving_result[1])

    dependant.cache_key = dependant.cache_key
    if dependant.use_cache and dependant.cache_key in dependency_cache:
        solved = dependency_cache[dependant.cache_key]
    else:
        solved = await concurrency.callable_to_coroutine(call, **solving_result[0])

    if dependant.name is not None:
        solved_values[dependant.name] = solved
    if dependant.cache_key not in dependency_cache:
        dependency_cache[dependant.cache_key] = solved


async def solve_dependencies(
    *,
    message: Message,
    dependant: Dependant,
    dependency_overrides_provider: Any = None,
    dependency_cache: Optional[Dict[CacheKey, Any]] = None,
) -> Tuple[Dict[str, Any], DependenciesCache]:
    """
    Resolve all required dependencies for Dependant using incoming message.

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
    solved_values: Dict[str, Any] = {}
    dependency_cache = dependency_cache or {}
    for sub_dependant in dependant.dependencies:
        await solve_sub_dependency(
            message=message,
            dependant=sub_dependant,
            solved_values=solved_values,
            dependency_overrides_provider=dependency_overrides_provider,
            dependency_cache=dependency_cache,
        )

    if dependant.message_param_name:
        solved_values[dependant.message_param_name] = message
    if dependant.bot_param_name:
        solved_values[dependant.bot_param_name] = message.bot
    if dependant.async_client_param_name:
        solved_values[dependant.async_client_param_name] = message.bot.client
    if dependant.sync_client_param_name:
        solved_values[dependant.sync_client_param_name] = message.bot.sync_client
    return solved_values, dependency_cache


def get_executor(
    dependant: Dependant,
    dependency_overrides_provider: Any = None,
) -> Callable[[Message], Awaitable[None]]:
    """Get an execution callable for passed dependency.

    Arguments:
        dependant: passed dependency for which execution callable should be generated.
        dependency_overrides_provider: dependency overrider that will be passed to the
            execution.

    Returns:
        Asynchronous executor for handling message.

    Raises:
        AssertionError: raised if there is no callable in `dependant.call`.
    """
    if dependant.call is None:
        raise AssertionError("dependant.call must be present")

    async def factory(message: Message) -> None:
        solved_values, _ = await solve_dependencies(
            message=message,
            dependant=dependant,
            dependency_overrides_provider=dependency_overrides_provider,
        )
        await concurrency.callable_to_coroutine(
            cast(Callable, dependant.call),
            **solved_values,
        )

    return factory
