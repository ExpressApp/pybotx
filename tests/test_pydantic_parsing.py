from typing import List, Union, Dict, Any

from pydantic import BaseModel, TypeAdapter

from pybotx.models.enums import StrEnum


class Types(StrEnum):
    A = "a"
    B = "b"
    C = "c"


class TestModel(BaseModel):
    type: Types
    data: str


class Event(BaseModel):
    entities: List[Union[TestModel, Dict[str, Any]]]


def test_parsing_union():
    # - Act -
    out = TypeAdapter(Event).validate_json(
        '{"entities": [{"type": "a", "data": "test"}, {"type": "d", "data": "test"}]}'
    )

    # - Assert -
    assert isinstance(out.entities[0], TestModel)
    assert isinstance(out.entities[1], dict)

