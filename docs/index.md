<h1 align="center">pybotx</h1>
<p align="center">
    <em>A little python framework for building bots for eXpress messenger.</em>
</p>
<p align="center">
    <a href=https://github.com/ExpressApp/pybotx>
        <img src=https://github.com/ExpressApp/pybotx/workflows/Tests/badge.svg alt="Tests" />
    </a>
    <a href=https://github.com/ExpressApp/pybotx>
        <img src=https://github.com/ExpressApp/pybotx/workflows/Styles/badge.svg alt="Styles" />
    </a>
    <a href="https://codecov.io/gh/ExpressApp/pybotx">
        <img src="https://codecov.io/gh/ExpressApp/pybotx/branch/master/graph/badge.svg" alt="Coverage" />
    </a>
    <a href="https://github.com/ambv/black">
        <img src="https://img.shields.io/badge/code%20style-black-000000.svg" alt="Code Style" />
    </a>
    <a href="https://pypi.org/project/botx/">
        <img src="https://badge.fury.io/py/botx.svg" alt="Package version" />
    </a>
    <a href="https://github.com/ExpressApp/pybotx/blob/master/LICENSE">
        <img src="https://img.shields.io/github/license/Naereen/StrapDown.js.svg" alt="License" />
    </a>
</p>


---

# Introduction

`pybotx` is a framework for building bots for eXpress providing a mechanism for simple
integration with your favourite asynchronous web frameworks.

Main features:

 * Simple integration with your web apps.
 * Asynchronous API with synchronous as a fallback option.
 * 100% test coverage.
 * 100% type annotated codebase.


!!! warning
    This library is under active development and its API may be unstable.
    Please lock the version you are using at the minor update level. For example, like this in `poetry`.

        [tool.poetry.dependencies]
        ...
        botx = "^0.15.0"
        ...

---

## Requirements

Python 3.7+

`pybotx` use the following libraries:

* <a href="https://github.com/samuelcolvin/pydantic" target="_blank">pydantic</a> for the data parts.
* <a href="https://github.com/encode/httpx" target="_blank">httpx</a> for making HTTP calls to BotX API.
* <a href="https://github.com/Delgan/loguru" target="_blank">loguru</a> for beautiful and powerful logs.
* **Optional**. <a href="https://github.com/encode/starlette" target="_blank">Starlette</a> for tests.

## Installation
```bash
$ pip install botx
```

Or if you are going to write tests:

```bash
$ pip install botx[tests]
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
{!./src/index/index0.py!}
```

* Deploy a bot on your server using uvicorn and set the url for the webhook in Express.
```bash
$ uvicorn main:app --host=0.0.0.0
```

This bot will send back every your message.

## License

This project is licensed under the terms of the MIT license.
