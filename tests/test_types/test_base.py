import json
import uuid
from uuid import UUID

import pytest
from pydantic import Schema

from botx.types.base import BotXType, UUIDJSONEncoder


def test_uuid_json_encoder():
    random_uuid = uuid.uuid4()
    random_dict = {i: ascii(i) for i in "some string"}
    assert UUIDJSONEncoder().encode(random_uuid) == json.dumps(str(random_uuid))
    assert UUIDJSONEncoder().encode(random_dict) == json.dumps(random_dict)
    with pytest.raises(TypeError):
        UUIDJSONEncoder().default(1)


def test_base_type():
    random_uuid = uuid.uuid4()

    class CustomType(BotXType):
        some_uuid_name: UUID = Schema(..., alias="another_uuid_name")

    assert CustomType(some_uuid_name=random_uuid).some_uuid_name == random_uuid
    assert CustomType(another_uuid_name=random_uuid).some_uuid_name == random_uuid
    assert CustomType(some_uuid_name=random_uuid).json() == json.dumps(
        {"another_uuid_name": str(random_uuid)}
    )
    assert CustomType(some_uuid_name=random_uuid).dict() == {
        "another_uuid_name": str(random_uuid)
    }
