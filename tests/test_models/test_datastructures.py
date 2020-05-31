import pytest

from botx.models.datastructures import State


def test_passed_state_applied():
    state = State({"a": 1})
    assert state.arg == 1


def test_state_can_be_set():
    state = State()
    state.arg = 1
    assert state.arg == 1


def test_state_will_raise_error_on_empty_attribute():
    state = State()
    with pytest.raises(AttributeError):
        _ = state.arg  # noqa: WPS122
