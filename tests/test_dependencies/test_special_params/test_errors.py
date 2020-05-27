import pytest


@pytest.fixture()
def handler_with_dependency(storage):
    def factory(_: int) -> None:
        """Just do nothing"""

    return factory


def test_error_for_wrong_param(bot, handler_with_dependency) -> None:
    with pytest.raises(ValueError):
        bot.default(handler_with_dependency)
