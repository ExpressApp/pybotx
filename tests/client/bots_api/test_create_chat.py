from http import HTTPStatus
from uuid import UUID

import httpx
import pytest
import respx

from botx import Bot, BotCredentials, HandlerCollector, lifespan_wrapper
from botx.bot.credentials_storage import CredentialsStorage
from botx.bot.models.commands.enums import ChatTypes


@pytest.fixture
def chat_id() -> UUID:
    return UUID("b46b18ee-88e8-452f-864a-993df921321e")


@respx.mock
@pytest.mark.asyncio
async def test_create_chat(
    httpx_client: httpx.AsyncClient,
    host: str,
    bot_id: UUID,
    bot_signature: str,
    bot_credentials: BotCredentials,
    prepared_credentials_storage: CredentialsStorage,
    chat_id: UUID,
) -> None:
    # - Arrange -
    endpoint = respx.post(
        f"https://{host}/api/v3/botx/chats/create",
        headers={"Authorization": "Bearer token", "Content-Type": "application/json"},
    ).mock(
        return_value=httpx.Response(
            HTTPStatus.OK,
            json={
                "status": "ok",
                "result": {"chat_id": str(chat_id)},
            },
        ),
    )

    built_bot = Bot(
        collectors=[HandlerCollector()],
        credentials=[],
        httpx_client=httpx_client,
    )
    # TODO: replace with bot_factory with prefilled token
    built_bot._botx_api_client._credentials_storage = (  # noqa: WPS437
        prepared_credentials_storage
    )

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        created_chat_id = await bot.create_chat(
            bot_id,
            "TEST_CHAT_NAME",
            ChatTypes.GROUP_CHAT,
            [],
        )

    # - Assert -
    assert created_chat_id == chat_id
    assert endpoint.called
