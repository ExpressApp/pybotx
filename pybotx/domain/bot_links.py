from __future__ import annotations

from typing import Any
from urllib.parse import urlencode
from uuid import UUID

from pybotx.domain.errors import InvalidBotCommandLinkError

DEFAULT_BOT_COMMAND_LINK_HOST = "xlnk.ms"
DEFAULT_BOT_COMMAND_LINK_SCHEME = "https"


def _normalize_base_url(*, host: str, scheme: str) -> str:
    base = host.strip()
    if not base:
        raise InvalidBotCommandLinkError("host must not be empty")
    if "://" in base:
        return base.rstrip("/")
    return f"{scheme}://{base}".rstrip("/")


def build_bot_command_link(
    *,
    huid: UUID | str,
    body: str | None = None,
    command: str | None = None,
    ets_id: str | None = None,
    host: str = DEFAULT_BOT_COMMAND_LINK_HOST,
    scheme: str = DEFAULT_BOT_COMMAND_LINK_SCHEME,
) -> str:
    """Build bot deeplink to open chat and optionally send a command.

    Format: https://xlnk.ms/open/bot/<huid>?ets_id=<string>&body=<string>&command=<string>
    `body` and `command` must be provided together or omitted together.
    """

    if (body is None) ^ (command is None):
        raise InvalidBotCommandLinkError(
            "body and command must be provided together",
        )

    base_url = _normalize_base_url(host=host, scheme=scheme)
    path = f"/open/bot/{huid}"

    query: dict[str, Any] = {}
    if ets_id is not None:
        query["ets_id"] = ets_id
    if body is not None and command is not None:
        query["body"] = body
        query["command"] = command

    if not query:
        return f"{base_url}{path}"

    return f"{base_url}{path}?{urlencode(query)}"


__all__ = ("build_bot_command_link",)
