<h1 align="center">pybotx</h1>
<p align="center">
    <em>A little python library for building bots for Express</em>
</p>
<p align="center">
    <a href="https://github.com/ExpressApp/pybotx/blob/master/LICENSE">
        <img src="https://img.shields.io/github/license/Naereen/StrapDown.js.svg" alt="License">
    </a>
    <a href="https://github.com/nsidnev/fastapi-realworld-example-app/blob/master/LICENSE">
        <img src="https://img.shields.io/badge/code%20style-black-000000.svg" alt="Code Style">
    </a>
    <a href="https://pypi.org/project/botx/">
        <img src="https://badge.fury.io/py/botx.svg" alt="Package version">
    </a>
</p>


---

# Introduction

`pybotx` is a toolkit for building bots for Express providing a mechanism for simple integration with your favourite web frameworks.

Main features:

 * Simple integration with your web apps.
 * Synchronous API as well as asynchronous.
 * 100% test coverage.
 * 100% type annotated codebase.

---

## Requirements

Python 3.6+

`pybotx` use the following libraries:

* <a href="https://github.com/samuelcolvin/pydantic" target="_blank">Pydantic</a> for the data parts.
* <a href="https://github.com/kennethreitz/requests" target="_blank">Requests</a> for making synchronous calls to BotX API.
* <a href="https://github.com/aio-libs/aiohttp" target="_blank">Aiohttp</a> for making asynchronous calls to BotX API.
* <a href="https://github.com/aio-libs/aiojobs" target="_blank">Aiojobs</a> for dispatching asynchronous tasks.

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
from botx import Bot, Message, Status
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.status import HTTP_202_ACCEPTED

bot = Bot(disable_credentials=True)


@bot.default_handler
def echo_handler(message: Message, bot: Bot):
    bot.answer_message(message.body, message)


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/status", response_model=Status, status_code=HTTP_202_ACCEPTED)
def bot_status():
    return bot.status


@app.post("/command")
def bot_command(message: Message):
    bot.execute_command(message.dict())
```
<details markdown="1">
<summary>Or use <code>async def</code></summary>

```Python3 hl_lines="1 6 10 11 23 24 28 33 34"
from botx import AsyncBot, Message, Status
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.status import HTTP_202_ACCEPTED

bot = AsyncBot(disable_credentials=True)


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

app.add_event_handler("startup", bot.start)
app.add_event_handler("shutdown", bot.stop)


@app.get("/status", response_model=Status, status_code=HTTP_202_ACCEPTED)
async def bot_status():
    return bot.status


@app.post("/command")
async def bot_command(message: Message):
    await bot.execute_command(message.dict())
```
</details>

* Deploy a bot on your server using uvicorn and set the url for the webhook in Express.
```bash
$ uvicorn main:app --host=0.0.0.0
```

This bot will send back every your message.

## License

This project is licensed under the terms of the MIT license.