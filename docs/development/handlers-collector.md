At some point you may decide that it is time to split your handlers into several files.
In order to make it as convenient as possible, `pybotx` provides a special mechanism that is similar to the mechanism
of routers from traditional web frameworks like `Blueprint`s in `Flask`.

Let's say you have a bot in the `bot.py` file that has many commands (public, hidden, next step) which can be divided into 3 groups:

 * commands to access `A` service.
 * commands to access `B` service.
 * general commands for handling files, saving user settings, etc.

Let's divide these commands in a following way:

 1. Leave the general commands in the `bot.py` file.
 2. Move the commands related to `A` service to the `a_commands.py` file.
 3. Move commands related to `B` service to the `b_commands.py` file.

### `HandlersCollector`

`HandlersCollector` is a class that can collect registered handlers in itself and then transfer them to bot.
In fact `Bot` is subclass of `HandlersCollector` so all methods available to `HandlersCollector` are also available to bots.


Using `HandlersCollector` is quite simple:

 1. Create an instance of the class.
 2. Register your handlers, just like you do it for your bot.
 3. Include registered handlers in your `Bot` instance using the `.include_handlers` method.

Here is an example.

If we have already divided our handlers into files, it will look something like this for the `a_commands.py` file:

```Python3
from botx import HandlersCollector, Message, Bot

collector = HandlersCollector()

@collector.handler
def my_handler_for_a(message: Message, bot: Bot):
    ...
```

And here is the `bot.py` file:

```Python3
from botx import Message, Bot

from a_commands import collector

bot = Bot(disable_credentials)
bot.include_handlers(collector)


@bot.default_handler
def default(message: Message, bot: Bot):
    ...
```

!!! warning

    If you try to add 2 handlers for the same command, `pybotx` will raise an exception indicating about merge error.
    If you still want to do this, you can set the `force_replace` argument to `True` in the `.include_handlers` method.
    This will replace the existing handler for the command with a new one without raising any error.

### Advanced handlers registration


In addition to the standard `.handler` method, `HandlersCollector` provides several other methods that may be useful to you.
These methods are just wrappers over the `.handler` method, but can reduce the amount of copy-paste when declaring handlers.
All these methods are used as decorators and all of them accept the callable object as their first (and some of them as the only) argument:

 * `HandlersCollector.handler` - is a most commonly used method to declare public handlers.
But it also provides some additional key arguments that can be used to change the behaviour of your handler:

    * `name: str = None` - the command name (useless field, maybe later will be use inside `pybotx`).
    * `description: str = None` - the description of the command that will be displayed in the status, default built by rule "`name` description".
    * `command: Union[str, Pattern] = None` - the body for the command for which the `Bot` instance will run the associated handler.
    * `commands: List[str, Pattern] = None` - list of command aliases that will also run handler execution.
    * `use_as_default_handler: bool = False` - indicates that the handler will be used in the absence of other handlers for the command.
    * `exclude_from_status: bool = False` - indicates that handler will not appear in the list of public commands.
    * `dependencies: List[Callable] = None` - list of background dependencies that will be executed before handler.
 * `HandlersCollector.hidden_command_handler` - is a `HandlersCollector.handler` with `exclude_from_status` set to `True` and removed
`description`, `use_as_default_handler` and `system_event_handler` arguments.
 * `HandlerCollector.file_handler` - is a handler for receiving files sent to the bot and it takes no additional arguments.
 The file will be placed in the `Message.file` property as the `File` class instance.
 * `HandlersCollector.default_handler` - is a handler for handling any commands that do not have associated handlers and also takes no additional arguments.
 * `HandlersCollector.system_event_handler` - is a handler for specific BotX API system commands with the reserved `system:` namespace.
 It requires a `event` key argument, which is the body of the command. See the example bellow.

    Predefined handlers for system events:

     * `HandlersCollector.chat_created_handler` - handles `system:chat_created` system event.

    If you want to register a handler for the `system:chat_created` system event using `HandlersCollector.system_event_handler`,
    you should register it as follows:

```Python3
from botx import SystemEventsEnum

...

@bot.system_event_handler(event=SystemEventsEnum.chat_created)
def handler(message: Message, bot: Bot):
    ...
```
