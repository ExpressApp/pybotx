from http import HTTPStatus
from typing import NoReturn
from uuid import UUID

import httpx
import pytest
import respx

from botx import (
    BotAccount,
    ExceptionNotRaisedInStatusHandlerError,
    InvalidBotXResponseError,
    InvalidBotXStatusCodeError,
)
from botx.bot.bot_accounts_storage import BotAccountsStorage
from botx.client.botx_method import BotXMethod
from botx.shared_models.api_base import (
    IncomingRequestBaseModel,
    OutgoingRequestBaseModel,
)


def incorrect_error_handler(response: httpx.Response) -> None:
    pass


def correct_error_handler(response: httpx.Response) -> NoReturn:
    raise ValueError("Some error")


class BotXAPIFooBarPayload(OutgoingRequestBaseModel):
    baz: int

    @classmethod
    def from_domain(cls, baz: int) -> "BotXAPIFooBarPayload":
        return cls(baz=baz)


class BotXAPIFooBar(IncomingRequestBaseModel):
    quux: int

    def to_domain(self) -> int:
        return self.quux


class FooBarMethod(BotXMethod):
    status_handlers = {
        # Wrong type just for test
        401: incorrect_error_handler,  # type: ignore
        403: correct_error_handler,
    }

    async def execute(self, payload: BotXAPIFooBarPayload) -> BotXAPIFooBar:
        path = "/foo/bar"

        response = await self._botx_method_call(
            "GET",
            self._build_url(path),
            params=payload.jsonable_dict(),
        )

        return self._extract_api_model(BotXAPIFooBar, response)


@respx.mock
@pytest.mark.asyncio
async def test__botx_method__exception_not_raised_in_status_handler_error_raised(
    httpx_client: httpx.AsyncClient,
    host: str,
    bot_id: UUID,
    bot_account: BotAccount,
) -> None:
    # - Arrange -
    endpoint = respx.get(f"https://{host}/foo/bar", params={"baz": 1}).mock(
        return_value=httpx.Response(HTTPStatus.UNAUTHORIZED),
    )

    method = FooBarMethod(
        bot_id,
        httpx_client,
        BotAccountsStorage([bot_account]),
    )
    payload = BotXAPIFooBarPayload.from_domain(baz=1)

    # - Act -
    with pytest.raises(ExceptionNotRaisedInStatusHandlerError):
        await method.execute(payload)

    # - Assert -
    assert endpoint.called


@respx.mock
@pytest.mark.asyncio
async def test__botx_method__invalid_botx_status_code_error_raised(
    httpx_client: httpx.AsyncClient,
    host: str,
    bot_id: UUID,
    bot_account: BotAccount,
) -> None:
    # - Arrange -
    endpoint = respx.get(f"https://{host}/foo/bar", params={"baz": 1}).mock(
        return_value=httpx.Response(HTTPStatus.METHOD_NOT_ALLOWED),
    )

    method = FooBarMethod(
        bot_id,
        httpx_client,
        BotAccountsStorage([bot_account]),
    )
    payload = BotXAPIFooBarPayload.from_domain(baz=1)

    # - Act -
    with pytest.raises(InvalidBotXStatusCodeError) as exc:
        await method.execute(payload)

    # - Assert -
    assert "failed with code 405" in str(exc)
    assert endpoint.called


@respx.mock
@pytest.mark.asyncio
async def test__botx_method__invalid_botx_response_error_raised(
    httpx_client: httpx.AsyncClient,
    host: str,
    bot_id: UUID,
    bot_account: BotAccount,
) -> None:
    # - Arrange -
    endpoint = respx.get(f"https://{host}/foo/bar", params={"baz": 1}).mock(
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
    payload = BotXAPIFooBarPayload.from_domain(baz=1)

    # - Act -
    with pytest.raises(InvalidBotXResponseError):
        await method.execute(payload)

    # - Assert -
    assert endpoint.called


@respx.mock
@pytest.mark.asyncio
async def test__botx_method__status_handler_called(
    httpx_client: httpx.AsyncClient,
    host: str,
    bot_id: UUID,
    bot_account: BotAccount,
) -> None:
    # - Arrange -
    endpoint = respx.get(f"https://{host}/foo/bar", params={"baz": 1}).mock(
        return_value=httpx.Response(HTTPStatus.FORBIDDEN),
    )

    method = FooBarMethod(
        bot_id,
        httpx_client,
        BotAccountsStorage([bot_account]),
    )
    payload = BotXAPIFooBarPayload.from_domain(baz=1)

    # - Act -
    with pytest.raises(ValueError) as exc:
        await method.execute(payload)

    # - Assert -
    assert "Some error" in str(exc)
    assert endpoint.called


@respx.mock
@pytest.mark.asyncio
async def test__botx_method__succeed(
    httpx_client: httpx.AsyncClient,
    host: str,
    bot_id: UUID,
    bot_account: BotAccount,
) -> None:
    # - Arrange -
    endpoint = respx.get(f"https://{host}/foo/bar", params={"baz": 1}).mock(
        return_value=httpx.Response(
            HTTPStatus.OK,
            json={"quux": 3},
        ),
    )

    method = FooBarMethod(
        bot_id,
        httpx_client,
        BotAccountsStorage([bot_account]),
    )
    payload = BotXAPIFooBarPayload.from_domain(baz=1)

    # - Act -
    botx_api_foo_bar = await method.execute(payload)

    # - Assert -
    assert botx_api_foo_bar.to_domain() == 3
    assert endpoint.called
