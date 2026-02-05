import secrets
import time
from enum import Enum
from typing import Optional
from uuid import UUID

import jwt


class BotXAuthVersion(str, Enum):
    V1 = "v1"
    V2 = "v2"


def build_botx_jwt_v2(
    *,
    bot_id: UUID,
    bot_host: str,
    secret_key: str,
    issued_at: Optional[int] = None,
    token_id: Optional[str] = None,
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

    return jwt.encode(payload=payload, key=secret_key, algorithm="HS256")
