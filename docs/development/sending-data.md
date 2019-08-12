`Bot` class from `pybotx` provide you 3 methods for sending message to the user (with some additional data) and 1 for sending the file:

* `.reply()` - send a message by passing a `ReplyMessage` instance.
* `.answer_message()` - send a message by passing text and the original message that was passed to the command handler.
* `.send_message()` - send message by passing text, `sync_id`, `group_chat_id` or list of them, `bot_id` and `host`. 
* `.send_file()` - send file using file-like object.

!!! info
    Note about using different values to send messages
    
    
    * `sync_id` is the `UUID` accosiated with the message in Express. You should use it only in command handlers.
    * `group_chat_id` - is the `UUID` accosiated with one of the chats in Express. In most cases, you should use it to 
    send messages, outside of handlers.
    

### Using `reply`

`Bot.reply` uses another method to send a message. Under the hood, he still uses `Bot.send_message` to perform send operations,
but provides a way for more easily create massive responses. It takes only 1 argument:

* `message: ReplyMessage` - is the <b>answer</b> message from bot

Here is an example of using this method outside from handler:

```Python3
async def some_function():
    reply = ReplyMessage(
        text="You were chosen by random.", 
        bot_id=BOT_ID, 
        host=CTS_HOST,
    )
    reply.chat_id = get_random_chat_id()
    await bot.reply(reply)
```

or inside command handler:

```Python3
@bot.handler
async def my_handler(message: Message, bot: Bot):
    reply = ReplyMessage.from_message("Answer from `.reply` method.", message)
    await bot.reply(reply)
```

### Send file

```python3
from botx import SendingCredentials
...
@bot.handler
async def my_handler(message: Message, bot: Bot):
    with open("file.txt") as f:
        file = File.from_file(f)

    await bot.send_file(
        file.file,
        SendingCredentials(
            sync_id=message.sync_id, bot_id=message.bot_id, host=message.host
        ),
    )
...
```

### Send file with message

!!! warning
    This feature is not supported yet on clients.

To attach a file to your message, simply pass it to the `file` argument for tje `Bot.send_message` or `Bot.answer_message` methods 
or use `ReplyMessage.add_file` if you use `Bot.reply`. This will create an instance of the `File` class that will be used to send result. 
If you want to use the same file several times, you can create a `File` object manually and use the `File.file` property to reuse the data.

```python3
@bot.handler
async def my_handler(message: Message, bot: Bot):
    with open("file.txt") as f:
        file = File.from_file(f)

    await bot.answer_message("Your file", message, file=file.file)

    reply = ReplyMessage.from_message("Your file (again)", message)
    reply.add_file(file)
    await bot.reply(reply)
...
```

### Add `Bubble` and `Keyboard`

You can attach bubbles or keyboard buttons to your message. 
A `Bubble` is a button that is stuck to your message. 
`Keyboard` is a panel that will be displayed when you click on the messege with the icon.

Adding these elements to your message is pretty easy. 
If you use the `.send_message` or `.answer_message` methods, you must pass a matrix of elements 
(`BubbleElement` or `KeyboardElement`) to corresponding arguments. Each array in this matrix will be a new row.

For example, if you want to add 3 buttons to a message (1 in the first line and 2 in the second):

```Python3
@bot.handler
async def my_handler(message: Message, bot: Bot):
    await bot.answer_message(
        "Bubble",
        message,
        bubble=[
            [BubbleElement(label="buble 1", command="")],
            [
                BubbleElement(label="buble 2", command=""),
                BubbleElement(label="buble 3", command=""),
            ],
        ],
    )
```

or add keyboard buttons using `.reply`:

```Python3
@bot.handler
async def my_handler(message: Message, bot: Bot):
    reply = ReplyMessage.from_message(message)
    reply.add_keyboard_button(command="", label="key 1")

    reply.add_keyboard_button(command="", label="key 1")
    reply.add_keyboard_button(command="", label="key 1", new_row=False)
    
    await bot.reply(reply)
```

### Mention users in message

You can mention users in your messages and they will receive notification from the chat, even if this chat was muted.

Using `.reply`:

```Python3
@bot.handler
async def my_handler(message: Message, bot: Bot):
    user_huid = get_random_user()

    reply = ReplyMessage.from_message(message)
    reply.mention_user(user_huid)
    
    await bot.reply(reply)
```

### Select Message Recipients

Similar to the mentions, you can specify the users who will receive your message by filling in `recipients` argument with list of users identifiers. 

### Change Notification Options

`Bot.send_message` and `Bot.answer_message` also take and additional argument `opts`, which is an instance of the `NotificationOpts` class 
and can control message delivery notifications.

`NotificationOpts` take the following arguments:

 * `send: bool` - send a push notification to the user, by default `True`.
 * `force_dnd` - ignore mute mode in chat with user, by default `False`.
 
Using `.reply`, it will look like this to disable the message delivery notification:

```Python3
@bot.handler
async def my_handler(message: Message, bot: Bot):
    reply = ReplyMessage.from_message(message)
    reply.show_notification(False)
    
    await bot.reply(reply)
```

or like this to ignore user's mute mode for the chat with the bot:

```Python3
@bot.handler
async def my_handler(message: Message, bot: Bot):
    reply = ReplyMessage.from_message(message)
    reply.force_notification(True)
    
    await bot.reply(reply)
```