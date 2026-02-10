from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class JwtEncoderPort(Protocol):
    def encode(
        self,
        payload: Mapping[str, Any],
        *,
        key: str | bytes | None = None,
        algorithm: str | None = None,
        headers: Mapping[str, Any] | None = None,
    ) -> str: ...  # pragma: no cover
