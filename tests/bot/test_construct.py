import pytest

from botx import Bot


def test_bot_require_at_least_one_collector() -> None:
    # - Act -
    with pytest.raises(ValueError) as exc:
        Bot(collectors=[])

    # - Assert -
    assert "at least one `HandlerCollector`" in str(exc)
