from typing import Dict
from uuid import UUID, uuid4

import pytest


@pytest.fixture()
def smartapp_api_version() -> int:
    return 1


@pytest.fixture()
def smartapp_counter() -> int:
    return 42


@pytest.fixture()
def smartapp_id() -> UUID:
    return uuid4()


@pytest.fixture()
def group_chat_id() -> UUID:
    return uuid4()


@pytest.fixture()
def ref() -> UUID:
    return uuid4()


@pytest.fixture()
def smartapp_data() -> Dict[str, str]:
    return {"key": "value"}
