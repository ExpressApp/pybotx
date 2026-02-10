from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any
from uuid import UUID

from pybotx.domain.errors import (
    RequestHeadersNotProvidedError,
    UnverifiedRequestError,
    UnknownBotAccountError,
)
from pybotx.domain.ports.bot_accounts_storage import BotAccountsStoragePort
from pybotx.domain.ports.jwt_verifier import JwtVerifierPort


class RequestVerifier:
    def __init__(
        self,
        *,
        bot_accounts_storage: BotAccountsStoragePort,
        jwt_verifier: JwtVerifierPort,
    ) -> None:
        self._bot_accounts_storage = bot_accounts_storage
        self._jwt_verifier = jwt_verifier

    def verify(
        self,
        headers: Mapping[str, str] | None,
        *,
        trusted_issuers: set[str] | None = None,
    ) -> None:
        if headers is None:
            raise RequestHeadersNotProvidedError

        authorization_header = headers.get("authorization")
        if not authorization_header:
            raise UnverifiedRequestError("The authorization token was not provided.")

        token = authorization_header.split()[-1]
        decode_algorithms = ["HS256"]

        token_payload = self._jwt_verifier.decode(
            token,
            algorithms=decode_algorithms,
            options={
                "verify_signature": False,
            },
        )
        if self._is_v2_payload(token_payload):
            self._verify_v2(token, token_payload, decode_algorithms)
        else:
            self._verify_v1(
                token,
                token_payload,
                decode_algorithms,
                trusted_issuers=trusted_issuers,
            )

    @staticmethod
    def _is_v2_payload(token_payload: Mapping[str, Any]) -> bool:
        if token_payload.get("version") == 2:
            return True

        audience = token_payload.get("aud")
        issuer = token_payload.get("iss")
        if not isinstance(audience, str) or not isinstance(issuer, str):
            return False

        try:
            UUID(issuer)
        except (TypeError, ValueError):
            return False

        return True

    def _verify_v2(
        self,
        token: str,
        token_payload: Mapping[str, Any],
        decode_algorithms: Sequence[str],
    ) -> None:
        issuer = token_payload.get("iss")
        if issuer is None:
            raise UnverifiedRequestError('Token is missing the "iss" claim')
        if not isinstance(issuer, str):
            raise UnverifiedRequestError("Invalid issuer")

        try:
            bot_id = UUID(issuer)
        except (TypeError, ValueError) as exc:
            raise UnverifiedRequestError("Invalid issuer") from exc

        try:
            bot_account = self._bot_accounts_storage.get_bot_account(bot_id)
        except UnknownBotAccountError as unknown_bot_exc:
            raise UnverifiedRequestError(unknown_bot_exc.args[0]) from unknown_bot_exc

        audience = token_payload.get("aud")
        if not audience or not isinstance(audience, str):
            raise UnverifiedRequestError("Invalid audience parameter was provided.")
        if audience != bot_account.host:
            raise UnverifiedRequestError("Invalid audience parameter was provided.")

        self._jwt_verifier.decode(
            token,
            key=bot_account.secret_key,
            algorithms=decode_algorithms,
            issuer=str(bot_account.id),
            audience=bot_account.host,
            leeway=1,
        )

    def _verify_v1(
        self,
        token: str,
        token_payload: Mapping[str, Any],
        decode_algorithms: Sequence[str],
        trusted_issuers: set[str] | None = None,
    ) -> None:
        audience = token_payload.get("aud")
        if (
            not audience
            or not isinstance(audience, Sequence)
            or isinstance(audience, str)
            or len(audience) != 1
        ):
            raise UnverifiedRequestError("Invalid audience parameter was provided.")

        try:
            bot_account = self._bot_accounts_storage.get_bot_account(UUID(audience[-1]))
        except UnknownBotAccountError as unknown_bot_exc:
            raise UnverifiedRequestError(unknown_bot_exc.args[0]) from unknown_bot_exc

        self._jwt_verifier.decode(
            token,
            key=bot_account.secret_key,
            algorithms=decode_algorithms,
            issuer=bot_account.host,
            leeway=1,
            options={
                "verify_aud": False,
                "verify_iss": False,
            },
        )

        issuer = token_payload.get("iss")
        if issuer is None:
            raise UnverifiedRequestError('Token is missing the "iss" claim')

        if issuer != bot_account.host:
            if not trusted_issuers or issuer not in trusted_issuers:
                raise UnverifiedRequestError("Invalid issuer")
