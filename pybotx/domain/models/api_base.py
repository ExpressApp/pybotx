import json
from typing import Any, cast

from pydantic import BaseModel, ConfigDict
from pydantic_core import to_jsonable_python

from pybotx.domain.missing import Undefined


def _remove_undefined(
    origin_obj: dict[str, Any] | list[Any],
) -> dict[str, Any] | list[Any]:
    if isinstance(origin_obj, dict):
        new_dict = {}

        for key, value in origin_obj.items():
            if value is Undefined:
                continue

            if isinstance(value, (list, dict)):
                new_value = _remove_undefined(value)
                if new_value or len(new_value) == len(value):
                    new_dict[key] = new_value
            else:
                new_dict[key] = value

        return new_dict

    if isinstance(origin_obj, list):
        new_list = []

        for value in origin_obj:
            if value is Undefined:
                continue

            if isinstance(value, (list, dict)):
                new_value = _remove_undefined(value)
                if new_value or len(new_value) == len(value):
                    new_list.append(new_value)
            else:
                new_list.append(value)

        return new_list

    raise NotImplementedError


class PayloadBaseModel(BaseModel):
    def json(self) -> str:  # type: ignore[override]
        clean_dict = _remove_undefined(self.model_dump())
        return json.dumps(clean_dict, default=to_jsonable_python, ensure_ascii=False)

    def jsonable_dict(self) -> dict[str, Any]:
        return cast(
            dict[str, Any],
            json.loads(self.json()),
        )


class VerifiedPayloadBaseModel(PayloadBaseModel):
    """Pydantic base model for API models."""


class UnverifiedPayloadBaseModel(PayloadBaseModel):
    def __init__(
        self,
        _fields_set: set[str] | None = None,
        **kwargs: Any,
    ) -> None:
        model = self.__class__.model_construct(_fields_set=_fields_set, **kwargs)
        self.__dict__.update(model.__dict__)

    model_config = ConfigDict(arbitrary_types_allowed=True)


__all__ = (
    "PayloadBaseModel",
    "UnverifiedPayloadBaseModel",
    "VerifiedPayloadBaseModel",
    "_remove_undefined",
)
