Getting started
===============

This API is tested with Python 3.7

1. Installation:
----------------

Installation using pip (a Python package manager)

.. code-block:: bash

    pip install botx

2. Requirements for bot
-----------------------

Bot requires 2 handlers for reserved endpoints:

 * ``GET`` `/status`
 * ``POST`` `/command`

3. Create simple echo-bot
-------------------------

Here we'll create a simple bot using ``fastapi`` that
will send back arguments from ``/echo`` command

3.1. Create and activate virtualenv for project
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    python -m venv venv
    source venv/bin/activate

3.2. Install dependecies
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    pip install botx fastapi uvicorn

3.3. Create file ``main.py``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python3

    from typing import Dict, Any
    from fastapi import FastAPI
    from botx import AsyncBot, Status

    bot = AsyncBot()

    @bot.command
    async def echo(message: Message, bot: AsyncBot):
        await bot.answer_message(message.command.cmd_arg, message)

    app = FastAPI()

    @app.get('/status', response_model=Status)
    async def status():
        return await bot.parse_status()

    @app.post('/command')
    async def command(data: Dict[str, Any]):
        return await bot.parse_command(data)

    @app.on_event('startup')
    async def on_startup():
        await bot.start()

    @app.on_event('shutdown')
    async def on_shutdown():
        await bot.stop()

3.4 Start bot with ``uvicorn``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    uvicorn main:app --reload
