import json
from enum import Enum
from typing import Any, Dict, cast

from pydantic import BaseModel


class APIBaseModel(BaseModel):
    """Pydantic base model for API models."""

    class Config:
        use_enum_values = True

    def jsonable_dict(self) -> Dict[str, Any]:
        # https://github.com/samuelcolvin/pydantic/issues/1409
        return cast(  # Pydantic model is always dict
            Dict[str, Any],
            json.loads(self.json()),
        )


class StrEnum(str, Enum):  # noqa: WPS600 (pydantic needs this inheritance)
    """Enum base for API models."""
