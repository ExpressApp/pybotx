import json
from enum import Enum
from typing import Any, Dict, Optional, Set, cast

from pydantic import BaseModel

from botx.missing import Undefined


def _remove_undefined_from_dict(origin_dict: Any) -> Dict[str, Any]:
    new_dict = {}
    for key, value in origin_dict.items():  # noqa: WPS110 (Normal name in this case)
        if value is Undefined:
            continue

        elif isinstance(value, dict):
            new_dict[key] = _remove_undefined_from_dict(value)
            continue

        new_dict[key] = value

    return new_dict


class VerifiedPayloadBaseModel(BaseModel):
    """Pydantic base model for API models."""

    class Config:
        use_enum_values = True


class UnverifiedPayloadBaseModel(BaseModel):
    def __init__(
        self,
        _fields_set: Optional[Set[str]] = None,
        **kwargs: Any,
    ) -> None:
        model = BaseModel.construct(_fields_set, **kwargs)
        self.__dict__.update(model.__dict__)  # noqa: WPS609 (Replace self attrs)

    class Config:
        arbitrary_types_allowed = True

    def jsonable_dict(self) -> Dict[str, Any]:
        # https://github.com/samuelcolvin/pydantic/issues/1409
        return cast(  # Pydantic model is always dict
            Dict[str, Any],
            json.loads(self.json()),
        )

    def dict(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return _remove_undefined_from_dict(super().dict(*args, **kwargs))


class StrEnum(str, Enum):  # noqa: WPS600 (pydantic needs this inheritance)
    """Enum base for API models."""
