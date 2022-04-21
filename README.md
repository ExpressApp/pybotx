# pybotx

*Библиотека для создания чат-ботов и SmartApps для мессенджера eXpress*

[![PyPI version](https://badge.fury.io/py/botx.svg)](https://badge.fury.io/py/pybotx)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pybotx)
[![Coverage](https://codecov.io/gh/ExpressApp/pybotx/branch/master/graph/badge.svg)](https://codecov.io/gh/ExpressApp/pybotx/branch/master)
[![Code style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)


## Особенности

* Простая для использования
* Поддерживает коллбэки BotX
* Легко интегрируется с асинхронными веб-фреймворками
* Полное покрытие тестами
* Полное покрытие аннотациями типов


## Установка

Используя `pip`:

```bash
pip install git+https://github.com/ExpressApp/pybotx.git
```

**Предупреждение:** Данный проект находится в активной разработке (`0.y.z`) и
его API может быть изменён при повышении минорной версии.


## Минимальный пример бота (интеграция с FastAPI)

```python
from http import HTTPStatus
from uuid import UUID

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from pybotx import (
    Bot,
    BotAccountWithSecret,
    HandlerCollector,
    IncomingMessage,
    build_command_accepted_response,
)

collector = HandlerCollector()


@collector.command("/echo", description="Send back the received message body")
async def echo_handler(message: IncomingMessage, bot: Bot) -> None:
    await bot.answer_message(message.body)


bot = Bot(
    collectors=[collector],
    bot_accounts=[
        BotAccountWithSecret(  # noqa: S106
            # Не забудьте заменить эти учётные данные на настоящие
            id=UUID("123e4567-e89b-12d3-a456-426655440000"),
            host="cts.example.com",
            secret_key="e29b417773f2feab9dac143ee3da20c5",
        ),
    ],
)

app = FastAPI()
app.add_event_handler("startup", bot.startup)
app.add_event_handler("shutdown", bot.shutdown)


@app.post("/command")
async def command_handler(request: Request) -> JSONResponse:
    bot.async_execute_raw_bot_command(await request.json())
    return JSONResponse(
        build_command_accepted_response(),
        status_code=HTTPStatus.ACCEPTED,
    )


@app.get("/status")
async def status_handler(request: Request) -> JSONResponse:
    status = await bot.raw_get_status(dict(request.query_params))
    return JSONResponse(status)


@app.post("/notification/callback")
async def callback_handler(request: Request) -> JSONResponse:
    bot.set_raw_botx_method_result(await request.json())
    return JSONResponse(
        build_command_accepted_response(),
        status_code=HTTPStatus.ACCEPTED,
    )
```
