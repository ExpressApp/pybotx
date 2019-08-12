By default, `pybotx` provides asynchronous methods through the `Bot` class, since this is more efficient. 
But as an alternative, you can import the `Bot` from the `botx.sync` module and use all the methods as normal blockable
functions. Handlers will then be dispatched using the `concurrent.futures.threads.ThreadPoolExecutor` object.


If you write synchronous handlers using the asynchronous `Bot` from the `botx` package, then you can call the client 
function to send data in the same way as if it were synchronous::

```python3
from botx import Bot, Message

bot = Bot()

@bot.handler
async def async_handler(message: Message, bot: Bot):
    await bot.answer_message(message.body, message)

@bot.handler
def sync_handler(message: Message, bot: Bot):
    bot.answer_message(message.body, message)

``` 