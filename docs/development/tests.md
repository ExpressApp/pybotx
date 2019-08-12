You can test the behaviour of your bot by writing unit tests. Since the main goal of the bot is to process commands and send 
results to the BotX API, you should be able  to intercept the result between sending data to the API. You can do this by setting 
`.asgi_app` attribute for `Bot.client` to an `ASGI` application instance. 
Then you write some mocks and test your logic inside tests. In this example we will use [`Starlette`](https://www.starlette.io/) to write mocks and `pytest` for unit tests.

## Example

### Bot

Suppose we have a bot that returns a message in the format `"Hello, {username}"` with the command `/hello`:

`bot.py`:
```python
from botx import Bot, Message

bot = Bot()


@bot.handler
async def hello(message: Message) -> None:
    await bot.answer_message(f"Hello, {message.username}", message)
```

### Helping utils

Let's write some utils for tests:

`utils.py`

```python
from typing import List, Any, Callable

from botx.models import (
    BotXFilePayload,
    BotXCommandResultPayload,
    BotXNotificationPayload,
)
from starlette.requests import Request
from starlette.responses import JSONResponse


def get_route(url: str) -> str:
    return url.split("{host}", 1)[1]


def get_test_route(array: List[Any]) -> Callable:
    async def testing_route(request: Request) -> JSONResponse:
        if request.headers["Content-Type"] != "application/json":
            form = await request.form()
            array.append((BotXFilePayload(**form), form["file"]))
        else:
            resp = await request.json()
            if "command" in request.url.path:
                array.append(BotXCommandResultPayload(**resp))
            else:
                array.append(BotXNotificationPayload(**resp))
        return JSONResponse()

    return testing_route
```

### Fixtures

Now let's write some fixtures to use them in our tests:

`conftest.py`: 
```python
from typing import Callable, Optional
from uuid import UUID, uuid4

import pytest
from botx import Bot, CTS, CTSCredentials, Message
from botx.core import BotXAPI
from starlette.applications import Starlette
from starlette.responses import JSONResponse

from .bot import bot
from .utils import get_route


@pytest.fixture
def bot_id() -> UUID:
    return uuid4()


@pytest.fixture
def host() -> str:
    return "cts.example.com"


@pytest.fixture
def get_botx_api_app() -> Callable:
    async def default_route(*_) -> JSONResponse:
        return JSONResponse({"status": "ok", "result": "result"})

    def _get_asgi_app(
            command_route: Optional[Callable] = None,
            notification_route: Optional[Callable] = None,
            file_route: Optional[Callable] = None,
    ) -> Starlette:
        app = Starlette()
        app.add_route(
            get_route(BotXAPI.V3.command.url),
            command_route or default_route,
            methods=[BotXAPI.V3.command.method],
        )
        app.add_route(
            get_route(BotXAPI.V3.notification.url),
            notification_route or default_route,
            methods=[BotXAPI.V3.notification.method],
        )
        app.add_route(
            get_route(BotXAPI.V1.file.url),
            file_route or default_route,
            methods=[BotXAPI.V1.file.method],
        )
        app.add_route(
            get_route(BotXAPI.V2.token.url),
            default_route,
            methods=[BotXAPI.V2.token.method],
        )

        return app

    return _get_asgi_app


@pytest.fixture
def get_bot(bot_id: UUID, host: str, get_botx_api_app: Callable) -> Callable:
    def _get_bot(
            *,
            command_route: Optional[Callable] = None,
            notification_route: Optional[Callable] = None,
            file_route: Optional[Callable] = None,
    ) -> Bot:
        bot.client.asgi_app = get_botx_api_app(
            command_route, notification_route, file_route
        )
        bot.add_cts(
            CTS(
                host=host,
                secret_key="secret",
                credentials=CTSCredentials(bot_id=bot_id, token="token"),
            )
        )

        return bot

    return _get_bot


@pytest.fixture
def message_data(bot_id: UUID, host: str) -> Callable:
    def _create_message_data(command: str) -> Message:
        command_body = {"body": command, "command_type": "user", "data": {}}

        data = {
            "bot_id": str(bot_id),
            "command": command_body,
            "file": None,
            "from": {
                "ad_login": "User Name",
                "ad_domain": "example.com",
                "chat_type": "chat",
                "group_chat_id": uuid4(),
                "host": host,
                "is_creator": True,
                "is_admin": True,
                "user_huid": uuid4(),
                "username": "testuser",
            },
            "sync_id": str(uuid4()),
        }

        return Message(**data)

    return _create_message_data
```

### Tests

Now we have fixtures for writing tests. Let's write a test to verify that the message body is in the required format:

`test_format_command.py`
```python
import pytest

from .utils import get_test_route

@pytest.mark.asyncio
async def test_hello_format(get_bot, create_message):
    result = []

    bot = get_bot(command_route=get_test_route(result))
    message = create_message('/hello')

    await bot.start()

    await bot.execute_command(message.dict())

    await bot.stop()

    assert result[0].command_result.body == 'Hello, testuser'
```