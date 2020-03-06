Let's create a new bot, which will ask the user for his data, and then send some statistics from the collected information.
Take echo-bot, from the [Introduction](../index.md), and gradually improve it step by step.

## Starting point

Right now we have the following code:

```Python3
{!./src/development/first_steps/first_steps0.py!}
```

## First, let's see how this code works
<small>We will explain only those parts that relate to `pybotx`, and not to the frameworks used in this documentation.</small>

### Step 1: import `Bot`, `Message`, `Status` and other classes

```Python3 hl_lines="1"
{!./src/development/first_steps/first_steps0.py!}
```

* [Bot][botx.bots.Bot] is a class that provides all the core functionality to your bots.
* [Message][botx.models.messages.Message] provides data to your handlers for commands.
* [Status][botx.models.menu.Status] is used here only to document the `FastAPI` route,
but in fact it stores information about public commands that user of your bot should see in menu.
* [ExpressServer][botx.models.credentials.ExpressServer] is used for storing information
about servers with which your bot is able to communicate.
* [IncomingMessage][botx.models.receiving.IncomingMessage] is a pydantic model that is used
for base validating of data, that was received on your bot's webhook.

### Step 2: initialize your `Bot`

```Python3 hl_lines="5"
{!./src/development/first_steps/first_steps0.py!}
```

The `bot` variable will be an "instance" of the class `Bot`.
We also register an instance of the cts server to get tokens and the ability to send requests to the API.

### Step 3: define default handler

```Python3 hl_lines="8"
{!./src/development/first_steps/first_steps0.py!}
```

This handler will be called for all commands that have not appropriate handlers.
We also set `include_in_status=False` so that handler won't be visible in menu and it won't
complain about "wrong" body generated for it automatically.

### Step 4: send text to user

```Python3 hl_lines="10"
{!./src/development/first_steps/first_steps0.py!}
```

[`.answer_message`][botx.bots.Bot.answer_message] will send text to the user by using
[sync_id][botx.models.messages.Message.sync_id], [bot_id][botx.models.messages.Message.bot_id]
and [host][botx.models.messages.Message.host] data from the [Message][botx.models.messages.Message] instance.
This is a simple wrapper for the [`.send`][botx.bots.Bot.send] method, which is used to
gain more control over sending messages process, allowing you to specify a different
host, bot_id, sync_id, group_chat_id or a list of them.

### Step 5: register handler for bot proper shutdown.

```Python3 hl_lines="14"
{!./src/development/first_steps/first_steps0.py!}
```

The [`.shutdown`][botx.bots.Bot.shutdown] method is used to stop pending handler.
You must call them to be sure that the bot will work properly.

### Step 6: define webhooks for bot

```Python3 hl_lines="17 22"
{!./src/development/first_steps/first_steps0.py!}
```

Here we define 2 `FastAPI` routes:

 * `GET` on `/status` will tell BotX API which commands are available for your bot.
 * `POST` on `/command` will receive data for incoming messages for your bot and execute handlers for commands.

!!! info

    If [`.execute_command`][botx.bots.Bot.execute_command] did not find a handler for
    the command in the message, it will raise an `NoMatch` error in background,
    which you probably want to [handle](./handling-errors.md). You can register default handler to process all commands that do not have their own handler.

### Step 7 (Improvement): Reply to user if message was received from host, which is not registered

We can send to BotX API a special response, that will say to user that bot can not communicate with
user properly, since message was received from unknown host. We do it by handling
[ServerUnknownError][botx.exceptions.ServerUnknownError] and returning to BotX API information
about error.

```Python3 hl_lines="35"
{!./src/development/first_steps/first_steps1.py!}
```

## Define new handlers

Let's define a new handler that will trigger a chain of questions for the user to collect information.

We'll use the `/fill-info` command to start the chain:

```Python3 hl_lines="14"
{!./src/development/first_steps/first_steps2.py!}
```

Here we define a new handler for `/fill-info` command using [`.handler`][botx.bots.Bot.handler] decorator.
This decorator will generate for us body for our command and register it doing it available to handle.
We also defined a `users_data` dictionary to store information from our users.

Now let's define another 2 handlers for the commands that were mentioned in the message text that we send to the user:

 * `/my-info` will just send the information that users have filled out about themselves.
 * `/info` will send back the number of users who filled in information about themselves, their average age and number of male and female users.
 * `/infomation` is an alias to `/info` command.

```Python3 hl_lines="32 50"
{!./src/development/first_steps/first_steps3.py!}
```

Take a look at highlighted lines. [`.handler`][botx.bots.Bot.handler] method takes a
different number of arguments. The most commonly used arguments are `command` and `commands`.
`command` is a single string that defines a command for a handler.
`commands` is a list of strings that can be used to define a variety of aliases for a handler.
You can use them together. In this case, they simply merge into one array as if you specified only `commands` argument.

See also at how the commands themselves are declared:

 * for the `fill_info` function we have not defined any `command` but it will be implicitly converted to the `/fill-info` command.
 * for the `get_info_for_user` function we had explicitly specified `/my-info` string.
 * for the `get_processed_information` we specified a `commands` argument to define many aliases for the handler.

## Register next step handlers

`pybotx` provide you the ability to change mechanism of handlers processing by mechanism of
middlewares. It also provides a middleware for handling chains of messages by [`Next Step Middleware`][botx.middlewares.ns.NextStepMiddleware].

To use it you should define functions that will be used when messages that start chain will be handled.
All functions should be defined before bot starts to handler messages, since dynamic registration
can cause different hard to find problems.

Lets' define these handlers and, finally, create a chain of questions from the bot to the user.

First we should import our middleware and functions that will register function fo next
message from user.

```Python3 hl_lines="2"
{!./src/development/first_steps/first_steps4.py!}
```

Next we should define our functions and register it in our middleware.

```Python3 hl_lines="11 17 36 51 52 53"
{!./src/development/first_steps/first_steps4.py!}
```

And the last part of this step is use
[register_next_step_handler][botx.middlewares.ns.register_next_step_handler] function to
register handler for next message from user.

```Python3 hl_lines="14 24 28 33 48 68"
{!./src/development/first_steps/first_steps4.py!}
```

### Recap

What's going on here? We added one line to our `/fill-info` command to start a chain of
questions for our user. We also defined 3 functions, whose signature is similar to the
usual handler signature, but instead of registration them using the
[`.handler`][botx.bots.Bot.handler] decorator, we do this while registering out
[`Next Step Middleware`][botx.middlewares.ns.NextStepMiddleware] for bot. We change message
handling flow using the [register_next_step_handler][botx.middlewares.ns.register_next_step_handler] function.
We pass into function our message as the first argument and the handler that will be
executed for the next user message as the second. We also can pass key arguments if we need them
and get them in our handler using [`Message state`][botx.models.datastructures.State] then, but this not our case now.
