from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from pybotx.domain.missing import Missing, Undefined
from pybotx.domain.models.async_files import File


@dataclass(slots=True)
class SyncSmartAppEventResult:
    data: Any
    files: Missing[list[File]] = Undefined


@dataclass(slots=True)
class SyncSmartAppEventError:
    reason: Missing[str] = Undefined
    errors: Missing[list[Any]] = Undefined
    error_data: Missing[dict[str, Any]] = Undefined


SyncSmartAppEventResponse = SyncSmartAppEventResult | SyncSmartAppEventError

__all__ = (
    "SyncSmartAppEventResult",
    "SyncSmartAppEventError",
    "SyncSmartAppEventResponse",
)
