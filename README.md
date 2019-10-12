<h1 align="center">pybotx</h1>
<p align="center">
    <em>A little python library for building bots for Express</em>
</p>
<p align="center">
    <a href="https://travis-ci.org/ExpressApp/pybotx">
        <img src="https://travis-ci.org/ExpressApp/pybotx.svg?branch=master" alt="Travis-CI">
    </a>
    <a href="https://github.com/ExpressApp/pybotx/blob/master/LICENSE">
        <img src="https://img.shields.io/github/license/Naereen/StrapDown.js.svg" alt="License">
    </a>
    <a href="https://github.com/ambv/black">
        <img src="https://img.shields.io/badge/code%20style-black-000000.svg" alt="Code Style">
    </a>
    <a href="https://pypi.org/project/botx/">
        <img src="https://badge.fury.io/py/botx.svg" alt="Package version">
    </a>
</p>


---

# Introduction

`pybotx` is a framework for building bots for Express providing a mechanism for simple integration with your favourite web frameworks.

Main features:

 * Simple integration with your web apps.
 * Asynchronous API with synchronous as a fallback option.
 * 100% test coverage.
 * 100% type annotated codebase.

**Note**: *This library is under active development and its API may be unstable. Please lock the version you are using at the minor update level. For example, like this in `poetry`.*
```
[tool.poetry.dependencies]
...
botx = "^0.12.0"
...
```
---

## Requirements

Python 3.6+

`pybotx` use the following libraries:

* <a href="https://github.com/samuelcolvin/pydantic" target="_blank">pydantic</a> for the data parts.
* <a href="https://github.com/encode/httpx" target="_blank">httpx</a> for making HTTP calls to BotX API.
* <a href="https://github.com/Delgan/loguru" target="_blank">loguru</a> for beautiful and powerful logs.

## Installation
```bash
$ pip install botx
```

You will also need a web framework to create bots as the current BotX API only works with webhooks.
This documentation will use <a href="https://github.com/tiangolo/fastapi" target="_blank">FastAPI</a> for the examples bellow.
```bash
$ pip install fastapi uvicorn
```

## Example

Let's create a simple echo bot.

* Create a file `main.py` with following content:
```Python3
from botx import Bot, CTS, Message, Status
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.status import HTTP_202_ACCEPTED

bot = Bot()
bot.add_cts(CTS(host="cts.example.com", secret_key="secret"))


@bot.default_handler
async def echo_handler(message: Message, bot: Bot):
    await bot.answer_message(message.body, message)


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/status", response_model=Status)
async def bot_status():
    return await bot.status()


@app.post("/command", status_code=HTTP_202_ACCEPTED)
async def bot_command(message: Message):
    await bot.execute_command(message.dict())
```

* Deploy a bot on your server using uvicorn and set the url for the webhook in Express.
```bash
$ uvicorn main:app --host=0.0.0.0
```

This bot will send back every your message.

## License

This project is licensed under the terms of the MIT license.
