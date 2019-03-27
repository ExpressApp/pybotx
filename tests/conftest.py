import base64
import json
from collections import OrderedDict
from typing import Any, Awaitable, Dict, NoReturn, Union

import aresponses
import pytest
import responses

from botx import CommandHandler, CommandRouter, RequestTypeEnum, Status
from botx.bot.basebot import BaseBot
from botx.bot.dispatcher.basedispatcher import BaseDispatcher
from botx.bot.dispatcher.syncdispatcher import SyncDispatcher
from botx.core import BotXAPI


@pytest.fixture
def sync_requests(hostname, bot_id):
    with responses.RequestsMock(assert_all_requests_are_fired=False) as mock:
        mock.add(
            BotXAPI.V2.token.method,
            BotXAPI.V2.token.url.format(host=hostname, bot_id=bot_id),
            json={"status": "ok", "result": "token_for_operations"},
        )
        mock.add(
            BotXAPI.V3.notification.method,
            BotXAPI.V3.notification.url.format(host=hostname),
            json={"status": "ok", "message": "notification_result_sent"},
        )
        mock.add(
            BotXAPI.V3.command.method,
            BotXAPI.V3.command.url.format(host=hostname),
            json={"status": "ok", "message": "command_result_sent"},
        )
        mock.add(
            BotXAPI.V1.file.method,
            BotXAPI.V1.file.url.format(host=hostname),
            json={"status": "ok", "message": "file_sent"},
        )
        yield mock


@pytest.fixture
def sync_error_requests(hostname, bot_id):
    with responses.RequestsMock(assert_all_requests_are_fired=False) as mock:
        mock.add(
            BotXAPI.V2.token.method,
            BotXAPI.V2.token.url.format(host=hostname, bot_id=bot_id),
            json={"status": "error", "message": " error response"},
            status=500,
        )
        mock.add(
            BotXAPI.V3.notification.method,
            BotXAPI.V3.notification.url.format(host=hostname),
            json={"status": "error", "message": " error response"},
            status=500,
        )
        mock.add(
            BotXAPI.V3.command.method,
            BotXAPI.V3.command.url.format(host=hostname),
            json={"status": "error", "message": " error response"},
            status=500,
        )
        mock.add(
            BotXAPI.V1.file.method,
            BotXAPI.V1.file.url.format(host=hostname),
            json={"status": "error", "message": " error response"},
            status=500,
        )
        yield mock


@pytest.fixture
async def async_requests(hostname, bot_id):
    mock: aresponses.ResponsesMockServer
    async with aresponses.ResponsesMockServer() as mock:
        mock.add(
            hostname,
            BotXAPI.V2.token.url.split("{host}", 1)[1].format(bot_id=bot_id),
            BotXAPI.V2.token.method.lower(),
            aresponses.Response(
                body=json.dumps({"status": "ok", "result": "token_for_operations"}),
                status=200,
            ),
        )
        mock.add(
            hostname,
            BotXAPI.V3.notification.url.split("{host}", 1)[1],
            BotXAPI.V3.notification.method.lower(),
            aresponses.Response(
                body=json.dumps({"status": "ok", "result": "notification_result_sent"}),
                status=200,
            ),
        )
        mock.add(
            hostname,
            BotXAPI.V3.command.url.split("{host}", 1)[1],
            BotXAPI.V3.command.method.lower(),
            aresponses.Response(
                body=json.dumps({"status": "ok", "result": "command_result_sent"}),
                status=200,
            ),
        )
        mock.add(
            hostname,
            BotXAPI.V1.file.url.split("{host}", 1)[1],
            BotXAPI.V1.file.method.lower(),
            aresponses.Response(
                body=json.dumps({"status": "ok", "result": "file_sent"}), status=200
            ),
        )
        yield mock


@pytest.fixture
async def async_error_requests(hostname, bot_id):
    mock: aresponses.ResponsesMockServer
    async with aresponses.ResponsesMockServer() as mock:
        mock.add(
            hostname,
            BotXAPI.V2.token.url.split("{host}", 1)[1].format(bot_id=bot_id),
            BotXAPI.V2.token.method.lower(),
            aresponses.Response(
                body=json.dumps({"status": "error", "message": " error response"}),
                status=500,
            ),
        )
        mock.add(
            hostname,
            BotXAPI.V3.notification.url.split("{host}", 1)[1],
            BotXAPI.V3.notification.method.lower(),
            aresponses.Response(
                body=json.dumps({"status": "error", "message": " error response"}),
                status=500,
            ),
        )
        mock.add(
            hostname,
            BotXAPI.V3.command.url.split("{host}", 1)[1],
            BotXAPI.V3.command.method.lower(),
            aresponses.Response(
                body=json.dumps({"status": "error", "message": " error response"}),
                status=500,
            ),
        )
        mock.add(
            hostname,
            BotXAPI.V1.file.url.split("{host}", 1)[1],
            BotXAPI.V1.file.method.lower(),
            aresponses.Response(
                body=json.dumps({"status": "error", "message": " error response"}),
                status=500,
            ),
        )
        yield mock


@pytest.fixture
def hostname():
    return "some.cts.ru"


@pytest.fixture
def bot_id():
    return "8dada2c8-67a6-4434-9dec-570d244e78ee"


@pytest.fixture
def secret():
    return "secret"


@pytest.fixture
def right_signature():
    return "904E39D3BC549C71F4A4BDA66AFCDA6FC90D471A64889B45CC8D2288E56526AD"


@pytest.fixture
def user(hostname):
    return {
        "user_huid": "a896e9ce-ab02-4927-8bca-51c2d3d0bda5",
        "group_chat_id": "cac806e0-4fea-4cd8-aafc-95e7129350e0",
        "ad_login": "test_user",
        "ad_domain": "test.com",
        "username": "Test",
        "chat_type": "group_chat",
        "host": hostname,
    }


@pytest.fixture
def binary_img_file():
    with open("tests/files/file.png", "rb") as f:
        return {
            "data": f"data:image/png;base64,{base64.b64encode(f.read()).decode()}",
            "file_name": "file.png",
        }


@pytest.fixture
def binary_gif_file():
    with open("tests/files/file.gif", "rb") as f:
        return {
            "data": f"data:image/gif;base64,{base64.b64encode(f.read()).decode()}",
            "file_name": "file.gif",
        }


@pytest.fixture
def text_txt_file():
    with open("tests/files/file.txt", "r") as f:
        return {
            "data": f"data:text/plain;base64,{base64.b64encode(f.read().encode()).decode()}",
            "file_name": "file.txt",
        }


@pytest.fixture
def text_json_file():
    with open("tests/files/file.json", "r") as f:
        return {
            "data": f"data:application/json;base64,{base64.b64encode(f.read().encode()).decode()}",
            "file_name": "file.json",
        }


@pytest.fixture
def command_with_text_and_file(text_json_file, user, bot_id):
    return {
        "sync_id": "a465f0f3-1354-491c-8f11-f400164295cb",
        "command": {"body": "/cmd arg", "data": {}},
        "file": text_json_file,
        "from": user,
        "bot_id": bot_id,
    }


@pytest.fixture
def custom_dispatcher():
    class CustomDispatcher(BaseDispatcher):
        def start(self) -> NoReturn:
            ...

        def shutdown(self) -> NoReturn:
            ...

        def parse_request(
            self, data: Dict[str, Any], request_type: Union[str, RequestTypeEnum]
        ) -> Union[Status, bool]:
            ...

        def _create_message(self, data: Dict[str, Any]) -> Union[Awaitable, bool]:
            ...

    return CustomDispatcher(None)


@pytest.fixture
def custom_handler():
    return CommandHandler(
        name="handler",
        command="/cmd",
        description="command handler",
        func=lambda x, b: ...,
    )


@pytest.fixture
def custom_async_handler():
    async def f(m, b):
        ...

    return CommandHandler(
        name="async handler", command="/acmd", description="command handler", func=f
    )


@pytest.fixture
def custom_async_handler_with_sync_command_body():
    async def f(m, b):
        pass

    return CommandHandler(
        name="async handler", command="/cmd", description="command handler", func=f
    )


@pytest.fixture
def custom_default_handler():
    return CommandHandler(
        name="default handler",
        command="/defaultcmd",
        description="default command handler",
        func=lambda x, y: ...,
        use_as_default_handler=True,
    )


@pytest.fixture
def custom_default_async_handler():
    async def f(m, b):
        pass

    return CommandHandler(
        name="default handler",
        command="/defaultcmd",
        description="default command handler",
        func=f,
        use_as_default_handler=True,
    )


@pytest.fixture
def custom_router():
    return CommandRouter()


@pytest.fixture
def custom_base_bot_class():
    class CustomBot(BaseBot):
        def __init__(self, **data):
            super().__init__(**data)
            self._dispatcher = SyncDispatcher(workers=1, bot=self)

        def stop(self):
            ...

        def parse_status(self):
            ...

        def parse_command(self, **kwargs):
            ...

        def _obtain_token(self, **kwargs):
            ...

        def send_message(self, **kwargs):
            ...

        def answer_message(self, **kwargs):
            ...

        def _send_command_result(self, **kwargs):
            ...

        def _send_notification_result(self, **kwargs):
            ...

        def send_file(self, **kwargs):
            ...

    return CustomBot
