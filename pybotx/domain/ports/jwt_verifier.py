from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class JwtVerifierPort(Protocol):
    def decode(
        self,
        token: str,
        *,
        key: str | None = None,
        algorithms: Sequence[str] | None = None,
        issuer: str | None = None,
        audience: str | Sequence[str] | None = None,
        options: Mapping[str, Any] | None = None,
        leeway: int | float | None = None,
    ) -> Mapping[str, Any]: ...  # pragma: no cover
