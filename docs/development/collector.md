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

### Collector

[Collector][botx.collecting.Collector] is a class that can collect registered handlers 
inside itself and then transfer them to bot.

Using [Collector][botx.collecting.Collector] is quite simple:

 1. Create an instance of the collector.
 2. Register your handlers, just like you do it for your bot.
 3. Include registered handlers in your [Bot][botx.bots.Bot] instance using the [`.include_collector`][botx.bots.Bot.include_collector] method.

Here is an example.

If we have already divided our handlers into files, it will look something like this for the `a_commands.py` file:

```Python3
{!./src/development/collector/collector0/a_commands.py!}
```

And here is the `bot.py` file:

```Python3
{!./src/development/collector/collector0/bot.py!}
```

!!! warning

    If you try to add 2 handlers for the same command, `pybotx` will raise an exception indicating about merge error.

### Advanced handlers registration

There are different methods for handlers registration available on [Collector][botx.collecting.Collector] and [Bot][botx.bots.Bot] instances.
You can register:

* regular handlers using [`.handler`][botx.collecting.Collector.handler] decorator.
* default handlers, that will be used if matching handler was not found using [`.default`][botx.collecting.Collector.default] decorator.
* hidden handlers, that won't be showed in bot's menu using [`.hidden`][botx.collecting.Collector.hidden] decorator.
* system event handlers, that will be used for handling special events from BotX API using [`.system_event`][botx.collecting.Collector.system_event] decorator.
* and some other type of handlers. See API reference for bot or collector for more information.
