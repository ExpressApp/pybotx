from enum import Enum

from pydantic import BaseModel


class APIBaseModel(BaseModel):
    """Pydantic base model for API models."""

    class Config:
        use_enum_values = True


class StrEnum(str, Enum):  # noqa: WPS600 (pydantic needs this inheritance)
    """Enum base for API models."""
