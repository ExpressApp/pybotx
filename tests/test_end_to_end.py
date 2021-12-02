import os
from http import HTTPStatus
from typing import List
from uuid import UUID

import pytest
from dotenv import load_dotenv
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route
from starlette.testclient import TestClient

from botx import (
    Bot,
    BotAccount,
    HandlerCollector,
    IncomingMessage,
    UnknownBotAccountError,
    build_accepted_response,
    build_bot_disabled_response,
)
from botx.logger import logger


def build_bot_accounts_from_env() -> List[BotAccount]:
    load_dotenv()

    bot_accounts = []
    for raw_credentials in os.environ["BOT_CREDENTIALS"].split(","):
        host, raw_bot_id, secret_key = raw_credentials.replace("|", "@").split("@")
        bot_accounts.append(
            BotAccount(host=host, bot_id=UUID(raw_bot_id), secret_key=secret_key),
        )

    return bot_accounts


# - pybotx -
collector = HandlerCollector()


@collector.command("/debug", description="Simple debug command")
async def debug_handler(message: IncomingMessage, bot: Bot) -> None:
    await bot.answer("Hi!")


bot_accounts = build_bot_accounts_from_env()
bot = Bot(collectors=[collector], bot_accounts=bot_accounts)


# - Starlette -
async def command_handler(request: Request) -> JSONResponse:
    try:
        bot.async_execute_raw_bot_command(await request.json())
    except ValueError:
        error_label = "Bot command validation error"
        logger.exception(error_label)

        return JSONResponse(
            build_bot_disabled_response(error_label),
            status_code=HTTPStatus.SERVICE_UNAVAILABLE,
        )
    except UnknownBotAccountError as exc:
        error_label = f"No credentials for bot {exc.bot_id}"
        logger.warning(error_label)

        return JSONResponse(
            build_bot_disabled_response(error_label),
            status_code=HTTPStatus.SERVICE_UNAVAILABLE,
        )

    return JSONResponse(build_accepted_response(), status_code=HTTPStatus.ACCEPTED)


async def status_handler(request: Request) -> JSONResponse:
    status = await bot.raw_get_status(dict(request.query_params))
    return JSONResponse(status)


async def callback_handler(request: Request) -> JSONResponse:
    bot.set_raw_botx_method_result(await request.json())
    return JSONResponse(build_accepted_response(), status_code=HTTPStatus.ACCEPTED)


app = Starlette(
    routes=[
        Route("/command", endpoint=command_handler, methods=["POST"]),
        Route("/status", endpoint=status_handler, methods=["GET"]),
        Route("/notification/callback", endpoint=callback_handler, methods=["POST"]),
    ],
    on_startup=[bot.startup],
    on_shutdown=[bot.shutdown],
)


# - tests -
@pytest.fixture
@pytest.mark.mock_authorization
def test_client() -> TestClient:
    return TestClient(app)


def test__web_app__bot_status(
    test_client: TestClient,
) -> None:
    response = test_client.get(
        "/status",
        params={
            "bot_id": "34477998-c8c7-53e9-aa4b-66ea5182dc3f",
            "chat_type": "chat",
            "user_huid": "f16cdc5f-6366-5552-9ecd-c36290ab3d11",
        },
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        "result": {
            "commands": [
                {
                    "body": "/debug",
                    "description": "Simple debug command",
                    "name": "/debug",
                },
            ],
            "enabled": True,
            "status_message": "Bot is working",
        },
        "status": "ok",
    }


def test__web_app__bot_command(
    test_client: TestClient,
) -> None:
    bot_id = str(bot_accounts[0].bot_id)
    payload = {
        "bot_id": bot_id,
        "command": {
            "body": "/hello",
            "command_type": "user",
            "data": {},
            "metadata": {},
        },
        "attachments": [],
        "async_files": [],
        "entities": [],
        "source_sync_id": None,
        "sync_id": "6f40a492-4b5f-54f3-87ee-77126d825b51",
        "from": {
            "ad_domain": None,
            "ad_login": None,
            "app_version": None,
            "chat_type": "chat",
            "device": None,
            "device_meta": {
                "permissions": None,
                "pushes": False,
                "timezone": "Europe/Moscow",
            },
            "device_software": None,
            "group_chat_id": "30dc1980-643a-00ad-37fc-7cc10d74e935",
            "host": "cts.example.com",
            "is_admin": True,
            "is_creator": True,
            "locale": "en",
            "manufacturer": None,
            "platform": None,
            "platform_package_id": None,
            "user_huid": "f16cdc5f-6366-5552-9ecd-c36290ab3d11",
            "username": None,
        },
        "proto_version": 4,
    }
    response = test_client.post(
        "/command",
        json=payload,
    )

    assert response.status_code == HTTPStatus.ACCEPTED


def test__web_app__unknown_bot_response(
    test_client: TestClient,
) -> None:
    payload = {
        "bot_id": "123e4567-e89b-12d3-a456-426655440000",
        "command": {
            "body": "/hello",
            "command_type": "user",
            "data": {},
            "metadata": {},
        },
        "attachments": [],
        "async_files": [],
        "entities": [],
        "source_sync_id": None,
        "sync_id": "6f40a492-4b5f-54f3-87ee-77126d825b51",
        "from": {
            "ad_domain": None,
            "ad_login": None,
            "app_version": None,
            "chat_type": "chat",
            "device": None,
            "device_meta": {
                "permissions": None,
                "pushes": False,
                "timezone": "Europe/Moscow",
            },
            "device_software": None,
            "group_chat_id": "30dc1980-643a-00ad-37fc-7cc10d74e935",
            "host": "cts.example.com",
            "is_admin": True,
            "is_creator": True,
            "locale": "en",
            "manufacturer": None,
            "platform": None,
            "platform_package_id": None,
            "user_huid": "f16cdc5f-6366-5552-9ecd-c36290ab3d11",
            "username": None,
        },
        "proto_version": 4,
    }
    response = test_client.post(
        "/command",
        json=payload,
    )

    assert response.status_code == HTTPStatus.SERVICE_UNAVAILABLE


def test__web_app__disabled_bot_response(
    test_client: TestClient,
) -> None:
    response = test_client.post(
        "/command",
        json={"incorrect": "request"},
    )

    assert response.status_code == HTTPStatus.SERVICE_UNAVAILABLE
    assert response.json() == {
        "error_data": {"status_message": "Bot command validation error"},
        "errors": [],
        "reason": "bot_disabled",
    }
