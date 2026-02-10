from uuid import UUID

import jwt
import pytest

from pybotx.domain.errors import JwtEncodingError
from pybotx.infrastructure.auth import build_botx_jwt_v2
from pybotx.infrastructure.jwt_encoder import PyJwtEncoder


class DummyEncoder:
    def __init__(self) -> None:
        self.calls: list[
            tuple[
                dict[str, object],
                str | bytes | None,
                str | None,
                dict[str, object] | None,
            ]
        ] = []

    def encode(
        self,
        payload: dict[str, object],
        *,
        key: str | bytes | None = None,
        algorithm: str | None = None,
        headers: dict[str, object] | None = None,
    ) -> str:
        self.calls.append((payload, key, algorithm, headers))
        return "token"


def test__build_botx_jwt_v2__uses_encoder_and_payload() -> None:
    encoder = DummyEncoder()
    bot_id = UUID("24348246-6791-4ac0-9d86-b948cd6a0e46")
    token = build_botx_jwt_v2(
        bot_id=bot_id,
        bot_host="cts.example.com",
        secret_key="secret",
        jwt_encoder=encoder,
        issued_at=100,
        token_id="token-id",
    )

    assert token == "token"
    assert encoder.calls == [
        (
            {
                "iss": str(bot_id),
                "aud": "cts.example.com",
                "exp": 160,
                "nbf": 100,
                "jti": "token-id",
                "iat": 100,
                "version": 2,
            },
            "secret",
            "HS256",
            None,
        ),
    ]


def test__pyjwt_encoder__encodes_token() -> None:
    encoder = PyJwtEncoder()
    token = encoder.encode(payload={"foo": "bar"}, key="secret", algorithm="HS256")
    decoded = jwt.decode(jwt=token, key="secret", algorithms=["HS256"])

    assert decoded["foo"] == "bar"


def test__pyjwt_encoder__wraps_error(monkeypatch: pytest.MonkeyPatch) -> None:
    encoder = PyJwtEncoder()

    def boom(*args, **kwargs):  # type: ignore[no-untyped-def]
        raise jwt.PyJWTError("boom")

    monkeypatch.setattr(jwt, "encode", boom)

    with pytest.raises(JwtEncodingError) as exc:
        encoder.encode(payload={"foo": "bar"}, key="secret", algorithm="HS256")

    assert "boom" in str(exc.value)
