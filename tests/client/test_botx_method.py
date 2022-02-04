from http import HTTPStatus
from uuid import UUID

import httpx
import pytest
from respx.router import MockRouter
from typing_extensions import Literal  # For python 3.7 support

from botx import (
    BotAccountWithSecret,
    InvalidBotXResponsePayloadError,
    InvalidBotXStatusCodeError,
)
from botx.bot.bot_accounts_storage import BotAccountsStorage
from botx.client.botx_method import BotXMethod, response_exception_thrower
from botx.client.exceptions.base import BaseClientError
from botx.models.api_base import UnverifiedPayloadBaseModel, VerifiedPayloadBaseModel


class FooBarError(BaseClientError):
    """Test exception."""


class BotXAPIFooBarRequestPayload(UnverifiedPayloadBaseModel):
    baz: int

    @classmethod
    def from_domain(cls, baz: int) -> "BotXAPIFooBarRequestPayload":
        return cls(baz=baz)


class BotXAPISyncIdResult(VerifiedPayloadBaseModel):
    sync_id: UUID


class BotXAPIFooBarResponsePayload(VerifiedPayloadBaseModel):
    status: Literal["ok"]
    result: BotXAPISyncIdResult

    def to_domain(self) -> UUID:
        return self.result.sync_id


class FooBarMethod(BotXMethod):
    status_handlers = {
        403: response_exception_thrower(FooBarError, "FooBar comment"),
    }

    async def execute(
        self,
        payload: BotXAPIFooBarRequestPayload,
    ) -> BotXAPIFooBarResponsePayload:
        path = "/foo/bar"

        response = await self._botx_method_call(
            "POST",
            self._build_url(path),
            json=payload.jsonable_dict(),
        )

        return self._verify_and_extract_api_model(
            BotXAPIFooBarResponsePayload,
            response,
        )


pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.usefixtures("respx_mock"),
]


async def test__botx_method__invalid_botx_status_code_error_raised(
    httpx_client: httpx.AsyncClient,
    respx_mock: MockRouter,
    host: str,
    bot_id: UUID,
    bot_account: BotAccountWithSecret,
) -> None:
    # - Arrange -
    endpoint = respx_mock.post(
        f"https://{host}/foo/bar",
        json={"baz": 1},
        headers={"Content-Type": "application/json"},
    ).mock(
        return_value=httpx.Response(HTTPStatus.METHOD_NOT_ALLOWED),
    )

    method = FooBarMethod(
        bot_id,
        httpx_client,
        BotAccountsStorage([bot_account]),
    )
    payload = BotXAPIFooBarRequestPayload.from_domain(baz=1)

    # - Act -
    with pytest.raises(InvalidBotXStatusCodeError) as exc:
        await method.execute(payload)

    # - Assert -
    assert "failed with code 405" in str(exc.value)
    assert endpoint.called


async def test__botx_method__invalid_json_raises_invalid_botx_response_payload_error(
    httpx_client: httpx.AsyncClient,
    respx_mock: MockRouter,
    host: str,
    bot_id: UUID,
    bot_account: BotAccountWithSecret,
) -> None:
    # - Arrange -
    endpoint = respx_mock.post(
        f"https://{host}/foo/bar",
        json={"baz": 1},
        headers={"Content-Type": "application/json"},
    ).mock(
        return_value=httpx.Response(
            HTTPStatus.OK,
            content='{"invalid": "json',
        ),
    )

    method = FooBarMethod(
        bot_id,
        httpx_client,
        BotAccountsStorage([bot_account]),
    )
    payload = BotXAPIFooBarRequestPayload.from_domain(baz=1)

    # - Act -
    with pytest.raises(InvalidBotXResponsePayloadError) as exc:
        await method.execute(payload)

    # - Assert -
    assert '{"invalid": "json' in str(exc.value)
    assert endpoint.called


async def test__botx_method__invalid_schema_raises_invalid_botx_response_payload_error(
    httpx_client: httpx.AsyncClient,
    respx_mock: MockRouter,
    host: str,
    bot_id: UUID,
    bot_account: BotAccountWithSecret,
) -> None:
    # - Arrange -
    endpoint = respx_mock.post(
        f"https://{host}/foo/bar",
        json={"baz": 1},
        headers={"Content-Type": "application/json"},
    ).mock(
        return_value=httpx.Response(
            HTTPStatus.OK,
            json={"invalid": "schema"},
        ),
    )

    method = FooBarMethod(
        bot_id,
        httpx_client,
        BotAccountsStorage([bot_account]),
    )
    payload = BotXAPIFooBarRequestPayload.from_domain(baz=1)

    # - Act -
    with pytest.raises(InvalidBotXResponsePayloadError) as exc:
        await method.execute(payload)

    # - Assert -
    assert '{"invalid": "schema"}' in str(exc.value)
    assert endpoint.called


async def test__botx_method__status_handler_called(
    httpx_client: httpx.AsyncClient,
    respx_mock: MockRouter,
    host: str,
    bot_id: UUID,
    bot_account: BotAccountWithSecret,
) -> None:
    # - Arrange -
    endpoint = respx_mock.post(
        f"https://{host}/foo/bar",
        json={"baz": 1},
        headers={"Content-Type": "application/json"},
    ).mock(
        return_value=httpx.Response(HTTPStatus.FORBIDDEN),
    )

    method = FooBarMethod(
        bot_id,
        httpx_client,
        BotAccountsStorage([bot_account]),
    )
    payload = BotXAPIFooBarRequestPayload.from_domain(baz=1)

    # - Act -
    with pytest.raises(FooBarError) as exc:
        await method.execute(payload)

    # - Assert -
    assert "403" in str(exc.value)
    assert "FooBar comment" in str(exc.value)
    assert endpoint.called


async def test__botx_method__succeed(
    httpx_client: httpx.AsyncClient,
    respx_mock: MockRouter,
    host: str,
    bot_id: UUID,
    bot_account: BotAccountWithSecret,
) -> None:
    # - Arrange -
    endpoint = respx_mock.post(
        f"https://{host}/foo/bar",
        json={"baz": 1},
        headers={"Content-Type": "application/json"},
    ).mock(
        return_value=httpx.Response(
            HTTPStatus.OK,
            json={
                "status": "ok",
                "result": {"sync_id": "21a9ec9e-f21f-4406-ac44-1a78d2ccf9e3"},
            },
        ),
    )

    method = FooBarMethod(
        bot_id,
        httpx_client,
        BotAccountsStorage([bot_account]),
    )
    payload = BotXAPIFooBarRequestPayload.from_domain(baz=1)

    # - Act -
    botx_api_foo_bar = await method.execute(payload)

    # - Assert -
    assert botx_api_foo_bar.to_domain() == UUID("21a9ec9e-f21f-4406-ac44-1a78d2ccf9e3")
    assert endpoint.called
