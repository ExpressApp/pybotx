from http import HTTPStatus
from uuid import UUID

import httpx
import pytest
import respx

from botx import (
    Bot,
    BotAccount,
    HandlerCollector,
    UnknownBotAccountError,
    lifespan_wrapper,
)


@pytest.fixture
def sync_id() -> UUID:
    return UUID("21a9ec9e-f21f-4406-ac44-1a78d2ccf9e3")


@respx.mock
@pytest.mark.asyncio
async def test__send__unknown_bot_account_error_raised(
    httpx_client: httpx.AsyncClient,
    host: str,
    sync_id: UUID,
    chat_id: UUID,
    bot_account: BotAccount,
    mock_authorization: None,
) -> None:
    # - Arrange -
    unknown_bot_id = UUID("51550ccc-dfd1-4d22-9b6f-a330145192b0")
    direct_notification_endpoint = respx.post(
        f"https://{host}/api/v3/botx/notification/callback/direct",
    )

    built_bot = Bot(
        collectors=[HandlerCollector()],
        bot_accounts=[bot_account],
        httpx_client=httpx_client,
    )

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        with pytest.raises(UnknownBotAccountError) as exc:
            await bot.send(
                "Hi!",
                bot_id=unknown_bot_id,
                chat_id=chat_id,
            )

    # - Assert -
    assert not direct_notification_endpoint.called
    assert str(unknown_bot_id) in str(exc)


@respx.mock
@pytest.mark.asyncio
async def test__send__succeed(
    httpx_client: httpx.AsyncClient,
    host: str,
    bot_id: UUID,
    sync_id: UUID,
    chat_id: UUID,
    bot_account: BotAccount,
    mock_authorization: None,
) -> None:
    # - Arrange -
    endpoint = respx.post(
        f"https://{host}/api/v3/botx/notification/callback/direct",
        headers={"Authorization": "Bearer token", "Content-Type": "application/json"},
        json={
            "group_chat_id": str(chat_id),
            "recipients": "all",
            "notification": {"status": "ok", "body": "Hi!"},
        },
    ).mock(
        return_value=httpx.Response(
            HTTPStatus.ACCEPTED,
            json={
                "status": "ok",
                "result": {"sync_id": str(sync_id)},
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
        message_id = await bot.send(
            "Hi!",
            bot_id=bot_id,
            chat_id=chat_id,
        )

    # - Assert -
    assert message_id == sync_id
    assert endpoint.called