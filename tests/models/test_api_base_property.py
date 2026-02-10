from typing import Any

from deepdiff import DeepDiff
from hypothesis import given, strategies as st

from pybotx.domain.missing import Undefined
from pybotx.infrastructure.contracts.api_base import PayloadBaseModel


class DummyPayload(PayloadBaseModel):
    payload: Any


def _contains_undefined(value: Any) -> bool:
    if value is Undefined:
        return True
    if isinstance(value, dict):
        return any(_contains_undefined(item) for item in value.values())
    if isinstance(value, list):
        return any(_contains_undefined(item) for item in value)
    return False


JSON_SCALARS = st.one_of(
    st.none(),
    st.booleans(),
    st.integers(),
    st.text(),
    st.floats(allow_nan=False, allow_infinity=False),
)

JSON_WITH_UNDEFINED = st.recursive(
    st.one_of(JSON_SCALARS, st.just(Undefined)),
    lambda children: st.lists(children, max_size=4)
    | st.dictionaries(st.text(min_size=1, max_size=10), children, max_size=4),
    max_leaves=10,
)


def test__payload_jsonable_dict__drops_undefined_values__deepdiff() -> None:
    payload = DummyPayload(
        payload={
            "a": 1,
            "b": Undefined,
            "c": {"d": Undefined, "e": 2},
            "f": [Undefined, 3, {"g": Undefined, "h": 4}],
        },
    )

    expected = {"payload": {"a": 1, "c": {"e": 2}, "f": [3, {"h": 4}]}}
    diff = DeepDiff(payload.jsonable_dict(), expected, ignore_order=True)
    assert diff == {}


@given(JSON_WITH_UNDEFINED)
def test__payload_jsonable_dict__no_undefined_values(payload: Any) -> None:
    model = DummyPayload(payload=payload)
    result = model.jsonable_dict()
    assert not _contains_undefined(result)
