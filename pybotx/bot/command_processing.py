from dataclasses import dataclass
from enum import Enum
from typing import Protocol

from pybotx.constants import (
    BOTX_COMMAND_PROCESSING_MAX_CONCURRENCY,
    BOTX_COMMAND_PROCESSING_MAX_QUEUE_SIZE,
)


class BotCommandOverloadAction(str, Enum):
    REJECT_NEW = "reject_new"
    DROP_OLDEST = "drop_oldest"


class BotCommandOverloadStrategy(Protocol):
    def on_queue_overflow(  # pragma: no cover
        self,
        *,
        queue_size: int,
        queue_max_size: int,
    ) -> BotCommandOverloadAction: ...


@dataclass(frozen=True, slots=True)
class RejectNewBotCommandOverloadStrategy(BotCommandOverloadStrategy):
    def on_queue_overflow(
        self,
        *,
        queue_size: int,
        queue_max_size: int,
    ) -> BotCommandOverloadAction:
        return BotCommandOverloadAction.REJECT_NEW


@dataclass(frozen=True, slots=True)
class DropOldestBotCommandOverloadStrategy(BotCommandOverloadStrategy):
    def on_queue_overflow(
        self,
        *,
        queue_size: int,
        queue_max_size: int,
    ) -> BotCommandOverloadAction:
        return BotCommandOverloadAction.DROP_OLDEST


@dataclass(frozen=True, slots=True)
class BotCommandProcessingConfig:
    max_concurrency: int = BOTX_COMMAND_PROCESSING_MAX_CONCURRENCY
    max_queue_size: int = BOTX_COMMAND_PROCESSING_MAX_QUEUE_SIZE
    overload_strategy: BotCommandOverloadStrategy | None = None

    def __post_init__(self) -> None:
        if self.max_concurrency < 1:
            raise ValueError(
                "Command processing max concurrency should be greater than 0",
            )
        if self.max_queue_size < 1:
            raise ValueError("Command processing max queue size should be greater than 0")

    def get_overload_strategy(self) -> BotCommandOverloadStrategy:
        return self.overload_strategy or RejectNewBotCommandOverloadStrategy()
