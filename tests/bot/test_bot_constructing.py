import pytest

from botx import Bot


def test__bot__required_at_least_one_collector() -> None:
    # - Act -
    with pytest.raises(ValueError) as exc:
        Bot(collectors=[], bot_accounts=[])

    # - Assert -
    assert "at least one `HandlerCollector`" in str(exc)
