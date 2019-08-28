import asyncio
import functools
import inspect
import json
import typing
from typing import Any, Callable, Dict, cast

from httpx.models import BaseResponse
from pydantic import ValidationError

from .exceptions import BotXValidationError
from .models import (
    BotXAPIErrorData,
    ChatCreatedData,
    CommandTypeEnum,
    ErrorResponseData,
    Message,
    SendingCredentials,
    SystemEventsEnum,
)

try:
    import contextvars  # Python 3.7+ only.
except ImportError:  # pragma: no cover
    contextvars = None  # type: ignore


def create_message(data: Dict[str, Any]) -> Message:
    try:
        message = Message(**data)

        if message.command.command_type == CommandTypeEnum.system:
            if message.body == SystemEventsEnum.chat_created.value:
                message.command.data = ChatCreatedData(
                    **cast(Dict[str, Any], message.command.data)
                )

        return message
    except ValidationError as exc:
        raise BotXValidationError from exc


def get_data_for_api_error(
    address: SendingCredentials, response: BaseResponse
) -> Dict[str, Any]:
    error_data = BotXAPIErrorData(
        address=address,
        response=ErrorResponseData(
            status_code=response.status_code, body=response.text
        ),
    )

    return json.loads(error_data.json())


async def run_in_threadpool(func: Callable, *args: Any, **kwargs: Any) -> typing.Any:
    loop = asyncio.get_event_loop()
    if contextvars is not None:  # pragma: no cover
        child = functools.partial(func, *args, **kwargs)
        context = contextvars.copy_context()
        func = context.run
        args = (child,)
    elif kwargs:  # pragma: no cover
        func = functools.partial(func, **kwargs)
    return await loop.run_in_executor(None, func, *args)


def is_coroutine_callable(call: Callable) -> bool:
    if inspect.isfunction(call):
        return asyncio.iscoroutinefunction(call)
    if inspect.isclass(call):
        return False
    call = getattr(call, "__call__", None)  # noqa: B004
    return asyncio.iscoroutinefunction(call)


async def call_function_as_coroutine(func: Callable, *args: Any, **kwargs: Any) -> Any:
    if is_coroutine_callable(func):
        return await func(*args, **kwargs)
    else:
        return await run_in_threadpool(func, *args, **kwargs)


def call_coroutine_as_function(func: Callable, *args: Any, **kwargs: Any) -> Any:
    coro = func(*args, **kwargs)

    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()

    if loop.is_running():
        return coro

    return loop.run_until_complete(coro)
