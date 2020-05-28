"""Shared config for pydantic dataclasses."""

from pydantic import BaseConfig


class BotXDataclassConfig(BaseConfig):
    """Config for pydantic dataclasses that allows custom types."""

    arbitrary_types_allowed = True
