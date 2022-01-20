# pybotx

*A python library for building bots and smartapps for eXpress messenger.*

[![PyPI version](https://badge.fury.io/py/botx.svg)](https://badge.fury.io/py/botx)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/botx)
[![Coverage](https://codecov.io/gh/ExpressApp/pybotx/branch/next/graph/badge.svg)](https://codecov.io/gh/ExpressApp/pybotx/branch/next)
[![Code style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)


## Features

* Designed to be ease to use
* Simple integration with async web-frameworks
* Support middlewares for command, command-collector and bot
* 100% test coverage
* 100% type annotated codebase


## Documentation

*TODO: Add link*
*TODO: Note that docs available only in Russian*


## Installation

Install pybotx using `pip`:

```bash
pip install git+https://github.com/ExpressApp/pybotx.git@next
```

*TODO: Add not about unstable version*


## Usage example

```python
from http import HTTPStatus
from uuid import UUID

from botx import (
    Bot,
    BotAccountWithSecret,
    ChatCreatedEvent,
    HandlerCollector,
    IncomingMessage,
    build_command_accepted_response,
)
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

collector = HandlerCollector()


@collector.chat_created
async def chat_created_handler(event: ChatCreatedEvent, bot: Bot) -> None:
    await bot.answer_message("Hello!")


@collector.command("/echo", description="Send back the received message body")
async def echo_handler(message: IncomingMessage, bot: Bot) -> None:
    await bot.answer_message(message.body)


@collector.default_message_handler
async def default_message_handler(event: IncomingMessage, bot: Bot) -> None:
    await bot.answer_message("Sorry, command not found.")


bot = Bot(
    collectors=[collector],
    bot_accounts=[
        BotAccountWithSecret(  # Replace fake account credentials with yours
            id=UUID("123e4567-e89b-12d3-a456-426655440000"),
            host="cts.example.com",
            secret_key="e29b417773f2feab9dac143ee3da20c5",
        )
    ],
)

app = FastAPI()
app.add_event_handler("startup", bot.startup)
app.add_event_handler("shutdown", bot.shutdown)


@app.post("/command")
async def command_handler(request: Request) -> JSONResponse:
    bot.async_execute_raw_bot_command(await request.json())
    return JSONResponse(
        build_command_accepted_response(), status_code=HTTPStatus.ACCEPTED
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
