import secrets
import time
from uuid import UUID

from pybotx.domain.auth import BotXAuthVersion
from pybotx.domain.ports.jwt_encoder import JwtEncoderPort

__all__ = ("BotXAuthVersion", "build_botx_jwt_v2")


def build_botx_jwt_v2(
    *,
    bot_id: UUID,
    bot_host: str,
    secret_key: str,
    jwt_encoder: JwtEncoderPort,
    issued_at: int | None = None,
    token_id: str | None = None,
) -> str:
    iat = int(time.time()) if issued_at is None else issued_at
    jti = token_id or secrets.token_hex(12)

    payload = {
        "iss": str(bot_id),
        "aud": bot_host,
        "exp": iat + 60,
        "nbf": iat,
        "jti": jti,
        "iat": iat,
        "version": 2,
    }

    return jwt_encoder.encode(payload=payload, key=secret_key, algorithm="HS256")
