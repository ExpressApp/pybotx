from http import HTTPStatus
from uuid import UUID

import httpx
import pytest
import respx

from botx import Bot, BotAccountWithSecret, HandlerCollector, lifespan_wrapper


@respx.mock
@pytest.mark.asyncio
@pytest.mark.mock_authorization
async def test__delete_sticker__succeed(
    httpx_client: httpx.AsyncClient,
    host: str,
    bot_id: UUID,
    bot_account: BotAccountWithSecret,
) -> None:
    # - Arrange -
    endpoint = respx.delete(
        f"https://{host}/api/v3/botx/stickers/"
        f"packs/26080153-a57d-5a8c-af0e-fdecee3c4435/"
        f"stickers/528c3953-5842-5a30-b2cb-8a09218497bc",
        headers={"Authorization": "Bearer token"},
    ).mock(
        return_value=httpx.Response(
            HTTPStatus.ACCEPTED,
            json={
                "status": "ok",
                "result": "delete_sticker_from_pack_pushed",
            },
        ),
    )

    built_bot = Bot(
        collectors=[HandlerCollector()],
        bot_accounts=[bot_account],
        httpx_client=httpx_client,
    )

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        await bot.delete_sticker(
            bot_id=bot_id,
            sticker_id=UUID("528c3953-5842-5a30-b2cb-8a09218497bc"),
            sticker_pack_id=UUID("26080153-a57d-5a8c-af0e-fdecee3c4435"),
        )

    # - Assert -
    assert endpoint.called
