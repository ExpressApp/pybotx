import pytest

from botx.missing import Undefined, not_undefined


def test__not_undefined__all_args_undefined() -> None:
    with pytest.raises(ValueError) as exc:
        not_undefined(Undefined, Undefined)

    assert "All arguments" in str(exc.value)
