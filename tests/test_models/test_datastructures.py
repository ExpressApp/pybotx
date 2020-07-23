import pytest

from botx.models.datastructures import State


class TestStateBehaviour:
    def test_passed_state_applied(self) -> None:
        state = State({"a": 1})
        assert state.a == 1

    def test_state_can_be_set(self) -> None:
        state = State()
        state.a = 1
        assert state.a == 1

    def test_state_will_raise_error_on_empty_attribute(self) -> None:
        state = State()
        with pytest.raises(AttributeError):
            _ = state.a
