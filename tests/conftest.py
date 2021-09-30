from http import HTTPStatus
from uuid import UUID

import httpx
import pytest
import respx

from botx import BotAccount


@pytest.fixture
def host() -> str:
    return "cts.example.com"


@pytest.fixture
def chat_id() -> UUID:
    return UUID("054af49e-5e18-4dca-ad73-4f96b6de63fa")


@pytest.fixture
def bot_id() -> UUID:
    return UUID("24348246-6791-4ac0-9d86-b948cd6a0e46")


@pytest.fixture
def bot_account(host: str, bot_id: UUID) -> BotAccount:
    return BotAccount(
        host=host,
        bot_id=bot_id,
        secret_key="bee001",
    )


@pytest.fixture
def mock_authorization(
    host: str,
    bot_id: UUID,
    bot_signature: str,
) -> None:
    respx.get(
        f"https://{host}/api/v2/botx/bots/{bot_id}/token",
        params={"signature": bot_signature},
    ).mock(
        return_value=httpx.Response(
            HTTPStatus.OK,
            json={
                "status": "ok",
                "result": "token",
            },
        ),
    )


@pytest.fixture
def bot_signature() -> str:
    return "E050AEEA197E0EF0A6E1653E18B7D41C7FDEC0FCFBA44C44FCCD2A88CEABD130"
