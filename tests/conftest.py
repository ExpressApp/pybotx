import base64
import logging
import pathlib
import random
import string
from uuid import UUID, uuid4

import aresponses
import pytest
import responses
from aiohttp.web_response import json_response
from loguru import logger

from botx import Message, ReplyMessage, SyncID, SystemEventsEnum
from botx.core import BotXAPI

from .utils import generate_user, generate_username, get_route_path_from_template


@pytest.fixture
def secret() -> str:
    return "".join(
        random.choice(string.ascii_letters) for _ in range(random.randrange(20, 30))
    )


@pytest.fixture(scope="session")
def host() -> str:
    return "cts.example.com"


@pytest.fixture(scope="session")
def bot_id() -> UUID:
    return uuid4()


@pytest.fixture
def sync_id() -> SyncID:
    return SyncID(uuid4())


@pytest.fixture
def gif_file_content() -> bytes:
    path = pathlib.Path(__file__).parent
    with open(path / "files" / "file.gif", "rb") as f:
        return f.read()


@pytest.fixture
def json_file_content() -> str:
    path = pathlib.Path(__file__).parent
    with open(path / "files" / "file.json", "r") as f:
        return f.read()


@pytest.fixture
def png_file_content() -> bytes:
    path = pathlib.Path(__file__).parent
    with open(path / "files" / "file.png", "rb") as f:
        return f.read()


@pytest.fixture
def txt_file_content() -> str:
    path = pathlib.Path(__file__).parent
    with open(path / "files" / "file.txt", "r") as f:
        return f.read()


@pytest.fixture
def chat_created_data():
    return {
        "group_chat_id": uuid4(),
        "chat_type": "group_chat",
        "name": "Test Chat",
        "creator": uuid4(),
        "members": [
            {
                "huid": uuid4(),
                "user_kind": random.choice(["user", "botx"]),
                "name": generate_username(),
                "admin": random.choice([True, False]),
            }
            for i in range(random.randrange(2, 6))
        ],
    }


@pytest.fixture
def message_data(
    bot_id: UUID, sync_id: SyncID, host: str, json_file_content, chat_created_data
):
    def _create_message_data(
        command: str = "/cmd",
        file: bool = True,
        admin: bool = False,
        chat_creator: bool = False,
    ):
        encoded_data = base64.b64encode(json_file_content.encode()).decode()

        file_data = (
            {
                "data": f"data:application/json;base64,{encoded_data}",
                "file_name": "file.json",
            }
            if file
            else None
        )

        command_body = {"body": command, "command_type": "user", "data": {}}

        if command == SystemEventsEnum.chat_created.value:
            command_body["data"] = chat_created_data
            command_body["command_type"] = "system"

        data = {
            "bot_id": str(bot_id),
            "command": command_body,
            "file": file_data,
            "from": generate_user(host, admin, chat_creator),
            "sync_id": str(sync_id),
        }
        return data

    return _create_message_data


@pytest.fixture
def reply_message(message_data) -> ReplyMessage:
    return ReplyMessage.from_message("text", Message(**message_data()))


@pytest.fixture
def handler_factory():
    def _create_handler(handler_type: str = "sync"):
        if handler_type == "sync":

            def sync_handler(*_) -> None:
                pass

            return sync_handler
        elif handler_type == "async":

            async def async_handler(*_) -> None:
                pass

            return async_handler
        else:
            raise ValueError("handler_type can be only 'sync' or 'async'")

    return _create_handler


@pytest.fixture(scope="session")
def valid_sync_requests_mock(host: str, bot_id: UUID) -> responses.RequestsMock:
    resp = {"status": "ok", "result": "result"}

    with responses.RequestsMock(assert_all_requests_are_fired=False) as mock:
        mock.add(
            BotXAPI.V2.token.method,
            BotXAPI.V2.token.url.format(host=host, bot_id=bot_id),
            json=resp,
        )

        mock.add(
            BotXAPI.V2.notification.method,
            BotXAPI.V2.notification.url.format(host=host),
            json=resp,
        )
        mock.add(
            BotXAPI.V2.command.method,
            BotXAPI.V2.command.url.format(host=host),
            json=resp,
        )

        mock.add(
            BotXAPI.V3.notification.method,
            BotXAPI.V3.notification.url.format(host=host),
            json=resp,
        )
        mock.add(
            BotXAPI.V3.command.method,
            BotXAPI.V3.command.url.format(host=host),
            json=resp,
        )

        mock.add(
            BotXAPI.V1.file.method, BotXAPI.V1.file.url.format(host=host), json=resp
        )

        yield mock


@pytest.fixture
async def valid_async_requests_mock(
    host: str, bot_id: UUID
) -> aresponses.ResponsesMockServer:
    resp = {"status": "ok", "result": "result"}

    async with aresponses.ResponsesMockServer() as mock:
        mock.add(
            host,
            get_route_path_from_template(BotXAPI.V2.token.url).format(bot_id=bot_id),
            BotXAPI.V2.token.method.lower(),
            json_response(resp),
        )

        mock.add(
            host,
            get_route_path_from_template(BotXAPI.V2.notification.url),
            BotXAPI.V2.notification.method.lower(),
            json_response(resp),
        )
        mock.add(
            host,
            get_route_path_from_template(BotXAPI.V2.command.url),
            BotXAPI.V2.command.method.lower(),
            json_response(resp),
        )

        mock.add(
            host,
            get_route_path_from_template(BotXAPI.V3.notification.url),
            BotXAPI.V3.notification.method.lower(),
            json_response(resp),
        )
        mock.add(
            host,
            get_route_path_from_template(BotXAPI.V3.command.url),
            BotXAPI.V3.command.method.lower(),
            json_response(resp),
        )

        mock.add(
            host,
            get_route_path_from_template(BotXAPI.V1.file.url),
            BotXAPI.V1.file.method.lower(),
            json_response(resp),
        )

        yield mock


@pytest.fixture
def wrong_sync_requests_mock(host: str, bot_id: UUID) -> responses.RequestsMock:
    resp = {"status": "error", "message": "error response"}

    with responses.RequestsMock(assert_all_requests_are_fired=False) as mock:
        mock.add(
            BotXAPI.V2.token.method,
            BotXAPI.V2.token.url.format(host=host, bot_id=bot_id),
            json=resp,
            status=500,
        )

        mock.add(
            BotXAPI.V2.notification.method,
            BotXAPI.V2.notification.url.format(host=host),
            json=resp,
            status=500,
        )
        mock.add(
            BotXAPI.V2.command.method,
            BotXAPI.V2.command.url.format(host=host),
            json=resp,
            status=500,
        )

        mock.add(
            BotXAPI.V3.notification.method,
            BotXAPI.V3.notification.url.format(host=host),
            json=resp,
            status=500,
        )
        mock.add(
            BotXAPI.V3.command.method,
            BotXAPI.V3.command.url.format(host=host),
            json=resp,
            status=500,
        )

        mock.add(
            BotXAPI.V1.file.method,
            BotXAPI.V1.file.url.format(host=host),
            json=resp,
            status=500,
        )

        yield mock


@pytest.fixture
async def wrong_async_requests_mock(
    host: str, bot_id: UUID
) -> aresponses.ResponsesMockServer:
    resp = {"status": "error", "message": "error response"}
    async with aresponses.ResponsesMockServer() as mock:
        mock.add(
            host,
            get_route_path_from_template(BotXAPI.V2.token.url).format(bot_id=bot_id),
            BotXAPI.V2.token.method.lower(),
            json_response(resp, status=500),
        )

        mock.add(
            host,
            get_route_path_from_template(BotXAPI.V2.notification.url),
            BotXAPI.V2.notification.method.lower(),
            json_response(resp, status=500),
        )
        mock.add(
            host,
            get_route_path_from_template(BotXAPI.V2.command.url),
            BotXAPI.V2.command.method.lower(),
            json_response(resp, status=500),
        )

        mock.add(
            host,
            get_route_path_from_template(BotXAPI.V3.notification.url),
            BotXAPI.V3.notification.method.lower(),
            json_response(resp, status=500),
        )
        mock.add(
            host,
            get_route_path_from_template(BotXAPI.V3.command.url),
            BotXAPI.V3.command.method.lower(),
            json_response(resp, status=500),
        )

        mock.add(
            host,
            get_route_path_from_template(BotXAPI.V1.file.url),
            BotXAPI.V1.file.method.lower(),
            json_response(resp, status=500),
        )

        yield mock


@pytest.fixture
def caplog(caplog):
    class PropogateHandler(logging.Handler):
        def emit(self, record):
            logging.getLogger(record.name).handle(record)

    handler_id = logger.add(PropogateHandler(), format="{message}")
    yield caplog
    logger.remove(handler_id)
