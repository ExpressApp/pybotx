from dataclasses import dataclass
from uuid import UUID

from pybotx.domain.models.message.edit_message import EditMessage
from pybotx.domain.models.message.outgoing_message import OutgoingMessage
from pybotx.domain.models.message.reply_message import ReplyMessage


@dataclass(slots=True)
class BulkSendItemResult:
    message: OutgoingMessage
    sync_id: UUID | None = None
    error: Exception | None = None

    @property
    def ok(self) -> bool:
        return self.error is None


@dataclass(slots=True)
class BulkSendResult:
    items: list[BulkSendItemResult]

    @property
    def successes(self) -> list[BulkSendItemResult]:
        return [item for item in self.items if item.ok]

    @property
    def failures(self) -> list[BulkSendItemResult]:
        return [item for item in self.items if not item.ok]


@dataclass(slots=True)
class BulkEditItemResult:
    message: EditMessage
    error: Exception | None = None

    @property
    def ok(self) -> bool:
        return self.error is None


@dataclass(slots=True)
class BulkEditResult:
    items: list[BulkEditItemResult]

    @property
    def successes(self) -> list[BulkEditItemResult]:
        return [item for item in self.items if item.ok]

    @property
    def failures(self) -> list[BulkEditItemResult]:
        return [item for item in self.items if not item.ok]


@dataclass(slots=True)
class BulkReplyItemResult:
    message: ReplyMessage
    error: Exception | None = None

    @property
    def ok(self) -> bool:
        return self.error is None


@dataclass(slots=True)
class BulkReplyResult:
    items: list[BulkReplyItemResult]

    @property
    def successes(self) -> list[BulkReplyItemResult]:
        return [item for item in self.items if item.ok]

    @property
    def failures(self) -> list[BulkReplyItemResult]:
        return [item for item in self.items if not item.ok]


__all__ = (
    "BulkSendItemResult",
    "BulkSendResult",
    "BulkEditItemResult",
    "BulkEditResult",
    "BulkReplyItemResult",
    "BulkReplyResult",
)
