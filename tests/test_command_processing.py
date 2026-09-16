import pytest

from pybotx import BotCommandProcessingConfig


def test__command_processing_config__invalid_max_concurrency_raises_value_error() -> None:
    with pytest.raises(
        ValueError,
        match="max concurrency should be greater than 0",
    ):
        BotCommandProcessingConfig(max_concurrency=0)


def test__command_processing_config__invalid_max_queue_size_raises_value_error() -> None:
    with pytest.raises(
        ValueError,
        match="max queue size should be greater than 0",
    ):
        BotCommandProcessingConfig(max_queue_size=0)
