"""Definition for protocol that owns collector instance."""
from botx.collecting.collectors.collector import Collector
from botx.typing import Protocol


class CollectorOwnerProtocol(Protocol):
    """Definition for protocol that owns collector instance."""

    @property
    def collector(self) -> Collector:
        """Collector with handlers."""
