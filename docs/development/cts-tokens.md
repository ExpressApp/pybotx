To use new features of the BotX API, you must prove that your bot is a real bot registered on the Express server.
You can do this by registering an instance of the `CTS` class with the `secret_key` for this bot in `Bot` or `AsyncBot` instances.

Here is a short example:

```Python3
from botx import Bot, CTS

host = 'cts.example.com'
secret_key = 'secret'

bot = Bot()
bot.add_cts(CTS(host=host, secret_key=secret_key))
```

It's all. From this point on, the `Bot` instance will use the BotX API routes with confirmation of the bot's credentials. 
That also means that for all hosts to which you will send messages, an instance of `CTS` class  must be registered `CTS`.