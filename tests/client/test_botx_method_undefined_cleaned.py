from http import HTTPStatus
from typing import Any, Dict
from uuid import UUID

import httpx
import pytest
import respx
from typing_extensions import Literal  # For python 3.7 support

from botx import BotAccountWithSecret
from botx.bot.bot_accounts_storage import BotAccountsStorage
from botx.client.botx_method import BotXMethod
from botx.missing import Undefined
from botx.models.api_base import UnverifiedPayloadBaseModel, VerifiedPayloadBaseModel


class BotXAPIFooBarRequestPayload(UnverifiedPayloadBaseModel):
    baz: Dict[str, Any]

    @classmethod
    def from_domain(cls, baz: Dict[str, Any]) -> "BotXAPIFooBarRequestPayload":
        return cls(baz=baz)


class BotXAPIFooBarResponsePayload(VerifiedPayloadBaseModel):
    status: Literal["ok"]


class FooBarMethod(BotXMethod):
    async def execute(
        self,
        payload: BotXAPIFooBarRequestPayload,
    ) -> None:
        path = "/foo/bar"

        response = await self._botx_method_call(
            "POST",
            self._build_url(path),
            json=payload.jsonable_dict(),
        )

        self._verify_and_extract_api_model(
            BotXAPIFooBarResponsePayload,
            response,
        )


@respx.mock
@pytest.mark.asyncio
async def test__botx_method__undefined_cleaned(
    httpx_client: httpx.AsyncClient,
    host: str,
    bot_id: UUID,
    bot_account: BotAccountWithSecret,
) -> None:
    # - Arrange -
    endpoint = respx.post(
        f"https://{host}/foo/bar",
        json={
            "baz": {
                "key": [
                    {
                        "key1": "value",
                        "key3": [1, 2, 3],
                        "key4": {"key1": "value"},
                        "key7": {},
                        "key8": [],
                    },
                ],
            },
        },
        headers={"Content-Type": "application/json"},
    ).mock(
        return_value=httpx.Response(
            HTTPStatus.OK,
            json={"status": "ok"},
        ),
    )

    method = FooBarMethod(
        bot_id,
        httpx_client,
        BotAccountsStorage([bot_account]),
    )
    payload = BotXAPIFooBarRequestPayload.from_domain(
        baz={
            "key": [
                {
                    "key1": "value",
                    "key2": Undefined,
                    "key3": [Undefined, 1, 2, Undefined, 3],
                    "key4": {"key1": "value", "key2": Undefined},
                    "key5": [Undefined, Undefined],
                    "key6": {"key1": Undefined, "key2": Undefined},
                    "key7": {},
                    "key8": [],
                },
                {
                    "key": Undefined,
                },
            ],
        },
    )

    # - Act -
    await method.execute(payload)

    # - Assert -
    assert endpoint.called
