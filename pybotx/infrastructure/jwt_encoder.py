from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import jwt

from pybotx.domain.errors import JwtEncodingError
from pybotx.domain.ports.jwt_encoder import JwtEncoderPort


class PyJwtEncoder(JwtEncoderPort):
    def encode(
        self,
        payload: Mapping[str, Any],
        *,
        key: str | bytes | None = None,
        algorithm: str | None = None,
        headers: Mapping[str, Any] | None = None,
    ) -> str:
        try:
            return jwt.encode(
                payload=payload,
                key=key,
                algorithm=algorithm,
                headers=headers,
            )
        except jwt.PyJWTError as exc:
            raise JwtEncodingError(str(exc)) from exc
