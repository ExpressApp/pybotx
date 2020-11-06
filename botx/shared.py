"""Shared config for pydantic dataclasses."""

from contextvars import ContextVar
from typing import Optional
from uuid import UUID

from pydantic import BaseConfig

debug_bot_id_var: ContextVar[Optional[UUID]] = ContextVar("debug_bot_id", default=None)


class BotXDataclassConfig(BaseConfig):
    """Config for pydantic dataclasses that allows custom types."""

    arbitrary_types_allowed = True
