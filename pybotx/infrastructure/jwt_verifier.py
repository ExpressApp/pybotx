from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

import jwt

from pybotx.domain.errors import UnverifiedRequestError
from pybotx.domain.ports.jwt_verifier import JwtVerifierPort


class PyJwtVerifier(JwtVerifierPort):
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
    ) -> Mapping[str, Any]:
        try:
            return jwt.decode(
                jwt=token,
                key=key,
                algorithms=list(algorithms) if algorithms is not None else None,
                issuer=issuer,
                audience=audience,
                options=options,
                leeway=leeway,
            )
        except jwt.InvalidTokenError as exc:
            raise UnverifiedRequestError(exc.args[0]) from exc
