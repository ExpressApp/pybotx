import logging
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, Union
from uuid import UUID

import aiohttp
import requests
from pydantic import ValidationError

from .core import BotXException
from .models import Message, SyncID

BOTX_LOGGER = logging.getLogger("botx")


def create_message(data: Dict[str, Any]) -> Message:
    try:
        return Message(**data)
    except ValidationError as exc:
        raise BotXException from exc


def get_headers(token: str) -> Dict[str, str]:
    return {"authorization": f"Bearer {token}"}


def thread_logger_wrapper(func: Callable) -> Callable:
    @wraps(func)
    def wrapper(message: Message, *args: Any, **kwargs: Any) -> None:
        try:

            # mypy has problems with callable with stars arguments; see #5876
            func(message, *args, **kwargs)  # type: ignore
        except Exception as exc:
            BOTX_LOGGER.exception(exc)

    return wrapper


def get_data_for_api_error_sync(
    host: str,
    bot_id: UUID,
    response: requests.Response,
    chat_ids: Optional[Union[SyncID, UUID, List[UUID]]] = None,
) -> Dict[str, Any]:
    data = {
        "host": host,
        "bot_id": str(bot_id),
        "response": {"status_code": response.status_code, "body": response.json()},
    }

    if chat_ids:
        if isinstance(chat_ids, (SyncID, UUID)):
            data["sync_id"] = str(chat_ids)
        else:
            if len(chat_ids) == 1:
                data["chat_id"] = str(chat_ids[0])
            else:
                data["chat_ids_list"] = [str(chat_id) for chat_id in chat_ids]

    return data


async def get_data_for_api_error_async(
    host: str,
    bot_id: UUID,
    response: aiohttp.client.ClientResponse,
    chat_ids: Optional[Union[SyncID, UUID, List[UUID]]] = None,
) -> Dict[str, Any]:
    data = {
        "host": host,
        "bot_id": str(bot_id),
        "response": {"status_code": response.status, "body": await response.json()},
    }

    if chat_ids:
        if isinstance(chat_ids, (SyncID, UUID)):
            data["sync_id"] = str(chat_ids)
        else:
            if len(chat_ids) == 1:
                data["chat_id"] = str(chat_ids[0])
            else:
                data["chat_ids_list"] = [str(chat_id) for chat_id in chat_ids]

    return data
