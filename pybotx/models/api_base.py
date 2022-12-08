import json
from typing import Any, Dict, List, Optional, Set, Union, cast

from pydantic import BaseModel
from pydantic.json import pydantic_encoder

from pybotx.missing import Undefined


def _remove_undefined(
    origin_obj: Union[Dict[str, Any], List[Any]],
) -> Union[Dict[str, Any], List[Any]]:
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

    elif isinstance(origin_obj, list):
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
    def json(self) -> str:  # type: ignore [override]
        clean_dict = _remove_undefined(self.dict())
        return json.dumps(clean_dict, default=pydantic_encoder, ensure_ascii=False)

    def jsonable_dict(self) -> Dict[str, Any]:
        return cast(
            Dict[str, Any],
            json.loads(self.json()),
        )


class VerifiedPayloadBaseModel(PayloadBaseModel):
    """Pydantic base model for API models."""


class UnverifiedPayloadBaseModel(PayloadBaseModel):
    def __init__(
        self,
        _fields_set: Optional[Set[str]] = None,
        **kwargs: Any,
    ) -> None:
        model = BaseModel.construct(_fields_set, **kwargs)
        self.__dict__.update(model.__dict__)  # noqa: WPS609 (Replace self attrs)

    class Config:
        arbitrary_types_allowed = True
