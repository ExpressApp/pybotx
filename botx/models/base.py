"""Module with base model classes."""
from pydantic import BaseModel


class BotXBaseModel(BaseModel):
    """Base class for configure all models."""

    class Config:
        use_enum_values = True
