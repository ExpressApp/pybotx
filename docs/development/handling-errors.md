`pybotx` provides a mechanism for registering a handler for exceptions that may occur in your command handlers. 
By default, these errors are simply logged to the console, but you can register different behavior and perform some actions.
For example, you can handle database disconnection or another runtime errors. You can also use this mechanism to 
register the handler for an `Excpetion` error and send info about it to the Sentry with additional information.

!!! info
    Exceptions from your error handlers will also be caught and propagated above. If there is no exception handler for error,
    it will simply logged, otherwise the registered handler will try to handle it.

## Usage Example

```python3
...

@bot.exception_catcher([RuntimeError])
async def error_handler(exc: Exception, msg: Message, bot: Bot):
    if message.body == "some action":
        await bot.send_message("this action will be fixed soon")
    ...
    
@bot.handler(command="cmd")
async def handler(message: Message, bot: Bot):
    ...
    if not cond:
        raise RuntimeError("error message")
    ...

...
```